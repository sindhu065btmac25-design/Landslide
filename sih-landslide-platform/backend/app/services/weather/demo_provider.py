"""Deterministic DEMO weather provider.

Per project requirement (§33): demo data must be clearly labeled, reproducible
and must simulate time progression — never presented as a real observation.
Determinism comes from hashing (lat, lon, hour-bucket) so the same location
produces the same demo reading within an hour, and a slow synthetic rainfall
build-up so judges can watch risk "increase" across a demo session.
"""
import hashlib
from datetime import datetime, timedelta, timezone

from app.schemas.common import DataStatus, Location, SourceEnvelope
from app.schemas.weather import CurrentWeather, HourlyForecastPoint, WeatherResponse


def _seed(location: Location, bucket: int) -> float:
    key = f"{location.latitude:.3f}:{location.longitude:.3f}:{bucket}"
    digest = hashlib.sha256(key.encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF  # 0..1


def build_demo_weather(location: Location) -> WeatherResponse:
    now = datetime.now(timezone.utc)
    hour_bucket = int(now.timestamp() // 3600)

    base = _seed(location, hour_bucket // 6)  # slow-moving weather regime
    jitter = _seed(location, hour_bucket)

    rainfall_24h = round(5 + base * 90 + jitter * 15, 1)
    rainfall_72h = round(rainfall_24h * (1.6 + jitter * 0.8), 1)

    hourly = []
    for h in range(-24, 24):
        t = now + timedelta(hours=h)
        hb = int(t.timestamp() // 3600)
        s = _seed(location, hb)
        hourly.append(
            HourlyForecastPoint(
                time=t.isoformat(),
                precipitation_mm=round(s * (rainfall_24h / 24) * 2, 2),
                precipitation_probability_pct=round(30 + s * 60, 1),
                soil_moisture_m3m3=round(0.15 + base * 0.25, 3),
            )
        )

    current = CurrentWeather(
        temperature_c=round(18 + jitter * 10, 1),
        relative_humidity_pct=round(60 + base * 35, 1),
        precipitation_mm=round(jitter * 8, 1),
        wind_speed_kmh=round(5 + jitter * 20, 1),
    )

    envelope = SourceEnvelope(
        status=DataStatus.DEMO,
        source="demo-weather-generator",
        observed_at=now,
        ingested_at=now,
        message="DEMO MODE — deterministic synthetic data, not a live observation.",
    )

    return WeatherResponse(
        location=location,
        envelope=envelope,
        current=current,
        hourly=hourly,
        rainfall_24h_mm=rainfall_24h,
        rainfall_72h_mm=rainfall_72h,
        precipitation_anomaly_pct=round((base - 0.5) * 100, 1),
    )

