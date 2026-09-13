"""Scheduled ingestion jobs. Each records an IngestionRun-shaped result dict
(started_at/completed_at/status/provider/records_processed/error) as required
by §17, with retry/backoff via Celery's autoretry mechanism."""
import asyncio
from datetime import datetime, timezone

from app.workers.celery_app import celery_app

# NER district reference points sampled for scheduled ingestion.
NER_SAMPLE_POINTS = [
    (26.14, 91.73, "Guwahati, Assam"),
    (25.57, 91.88, "Shillong, Meghalaya"),
    (27.08, 93.62, "Itanagar, Arunachal Pradesh"),
    (24.82, 93.94, "Imphal, Manipur"),
    (23.73, 92.72, "Agartala, Tripura"),
]


def _run_record(job_name: str, provider: str):
    return {"job_name": job_name, "provider": provider, "started_at": datetime.now(timezone.utc)}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_weather(self):
    from app.schemas.common import Location
    from app.services.weather.service import WeatherService

    record = _run_record("ingest_weather", "open-meteo")
    try:
        service = WeatherService()

        async def _run():
            results = []
            for lat, lon, name in NER_SAMPLE_POINTS:
                results.append(await service.get_weather(Location(latitude=lat, longitude=lon, name=name)))
            return results

        results = asyncio.run(_run())
        record.update(completed_at=datetime.now(timezone.utc), status="success", records_processed=len(results))
        return record
    except Exception as exc:  # noqa: BLE001
        record.update(completed_at=datetime.now(timezone.utc), status="error", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def ingest_satellite(self):
    from app.schemas.common import Location
    from app.services.satellite.service import SatelliteService

    record = _run_record("ingest_satellite", "sentinel-hub")
    try:
        service = SatelliteService()

        async def _run():
            results = []
            for lat, lon, name in NER_SAMPLE_POINTS:
                results.append(await service.get_change_summary(Location(latitude=lat, longitude=lon, name=name)))
            return results

        results = asyncio.run(_run())
        record.update(completed_at=datetime.now(timezone.utc), status="success", records_processed=len(results))
        return record
    except Exception as exc:  # noqa: BLE001
        record.update(completed_at=datetime.now(timezone.utc), status="error", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def ingest_soil_moisture(self):
    # Soil moisture is bundled into the Open-Meteo hourly pull in this
    # scaffold (see services/weather); kept as a separate task per spec §17
    # for when a dedicated soil-moisture provider is added.
    return ingest_weather.run()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=900)
def ingest_precipitation(self):
    return ingest_weather.run()

