from celery import Celery

from core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "landslide_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.ingestion_jobs", "workers.risk_jobs"],
)

celery_app.conf.beat_schedule = {
    "ingest-weather-every-15-min": {"task": "workers.ingestion_jobs.ingest_weather", "schedule": 900.0},
    "ingest-satellite-every-6-hours": {"task": "workers.ingestion_jobs.ingest_satellite", "schedule": 21600.0},
    "update-risk-every-30-min": {"task": "workers.risk_jobs.update_risk", "schedule": 1800.0},
    "generate-alerts-every-30-min": {"task": "workers.risk_jobs.generate_alerts", "schedule": 1800.0},
}
celery_app.conf.task_acks_late = True
celery_app.conf.task_default_retry_delay = 60
