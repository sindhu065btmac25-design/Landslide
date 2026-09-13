from pydantic import BaseModel

from schemas.common import Location, SourceEnvelope


class CurrentWeather(BaseModel):
    temperature_c: float | None = None
    relative_humidity_pct: float | None = None
    precipitation_mm: float | None = None
    wind_speed_kmh: float | None = None


class HourlyForecastPoint(BaseModel):
    time: str
    precipitation_mm: float | None = None
    precipitation_probability_pct: float | None = None
    soil_moisture_m3m3: float | None = None


class WeatherResponse(BaseModel):
    location: Location
    envelope: SourceEnvelope
    current: CurrentWeather | None = None
    hourly: list[HourlyForecastPoint] = []
    rainfall_24h_mm: float | None = None
    rainfall_72h_mm: float | None = None
    precipitation_anomaly_pct: float | None = None
