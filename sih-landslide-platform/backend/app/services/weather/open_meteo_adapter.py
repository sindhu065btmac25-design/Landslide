"""Real Open-Meteo adapter.

Open-Meteo requires no API key, so this adapter is "live-capable" purely on
network access. If the request fails (no network, timeout, bad response) we
return a structured UNAVAILABLE envelope — we never invent numbers.
"""
from datetime import datetime, timezone

import httpx

from app.core.config import get_settings
from app.schemas.common import DataStatus, Location, SourceEnvelope
from app.schemas.weather import CurrentWeather, HourlyForecastPoint, WeatherResponse

HOURLY_VARS = [
    "precipitation",
    "precipitation_probability",
    "soil_moisture_0_to_1cm",
    "temperature_2m",
    "relative_humidity_2m",
]


class OpenMeteoAdapter:
    """Adapter for https://open-meteo.com/ forecast API."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_current_and_forecast(self, location: Location) -> WeatherResponse:
        now = datetime.now(timezone.utc)
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "hourly": ",".join(HOURLY_VARS),
            "past_days": 3,
            "forecast_days": 3,
            "timezone": "UTC",
        }
        try:
            async with httpx.AsyncClient(timeout=self.settings.HTTP_TIMEOUT_SECONDS) as client:
                resp = await client.get(self.settings.OPEN_METEO_BASE_URL, params=params)
                resp.raise_for_status()
                payload = resp.json()
            return self._parse(location, payload, now)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            envelope = SourceEnvelope(
                status=DataStatus.UNAVAILABLE,
                source="open-meteo",
                ingested_at=now,
                message=f"Live weather fetch failed: {exc.__class__.__name__}: {exc}",
            )
            return WeatherResponse(location=location, envelope=envelope)

    def _parse(self, location: Location, payload: dict, now: datetime) -> WeatherResponse:
        current_raw = payload.get("current", {})
        current = CurrentWeather(
            temperature_c=current_raw.get("temperature_2m"),
            relative_humidity_pct=current_raw.get("relative_humidity_2m"),
            precipitation_mm=current_raw.get("precipitation"),
            wind_speed_kmh=current_raw.get("wind_speed_10m"),
        )

        hourly_raw = payload.get("hourly", {})
        times = hourly_raw.get("time", [])
        precip = hourly_raw.get("precipitation", [])
        precip_prob = hourly_raw.get("precipitation_probability", [])
        soil_moisture = hourly_raw.get("soil_moisture_0_to_1cm", [])

        hourly = []
        for i, t in enumerate(times):
            hourly.append(
                HourlyForecastPoint(
                    time=t,
                    precipitation_mm=precip[i] if i < len(precip) else None,
                    precipitation_probability_pct=precip_prob[i] if i < len(precip_prob) else None,
                    soil_moisture_m3m3=soil_moisture[i] if i < len(soil_moisture) else None,
                )
            )

        rainfall_24h = self._sum_last_n_hours(times, precip, now, 24)
        rainfall_72h = self._sum_last_n_hours(times, precip, now, 72)

        observed_at = current_raw.get("time")
        envelope = SourceEnvelope(
            status=DataStatus.LIVE,
            source="open-meteo",
            observed_at=observed_at,
            ingested_at=now,
        )

        return WeatherResponse(
            location=location,
            envelope=envelope,
            current=current,
            hourly=hourly,
            rainfall_24h_mm=rainfall_24h,
            rainfall_72h_mm=rainfall_72h,
        )

    @staticmethod
    def _sum_last_n_hours(times: list[str], precip: list[float], now: datetime, n: int) -> float | None:
        if not times or not precip:
            return None
        try:
            total = 0.0
            cutoff = now.timestamp() - n * 3600
            for t, p in zip(times, precip):
                ts = datetime.fromisoformat(t).replace(tzinfo=timezone.utc).timestamp()
                if ts >= cutoff and ts <= now.timestamp() and p is not None:
                    total += p
            return round(total, 2)
        except (ValueError, TypeError):
            return None

