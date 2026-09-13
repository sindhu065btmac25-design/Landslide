"""Central application configuration.

All external service configuration is read from environment variables.
Nothing sensitive is hardcoded. See /.env.example at repo root.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "NER Landslide Risk Intelligence Platform"
    MODEL_VERSION: str = "risk-fusion-0.1.0-rule-based"
    FEATURE_VERSION: str = "features-0.1.0"

    # Global mode switch. When a real provider has no usable credentials,
    # individual adapters fall back to DEMO for that layer only and report
    # status="demo" — this flag additionally allows forcing DEMO everywhere
    # for local development / judge demonstrations.
    DEMO_MODE: bool = True

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/landslide"
    REDIS_URL: str = "redis://localhost:6379/0"

    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"

    COPERNICUS_CLIENT_ID: str | None = None
    COPERNICUS_CLIENT_SECRET: str | None = None
    SENTINEL_HUB_BASE_URL: str = "https://sh.dataspace.copernicus.eu"

    NASA_GPM_TOKEN: str | None = None

    OVERPASS_BASE_URL: str = "https://overpass-api.de/api/interpreter"

    JWT_SECRET: str = "change-me-in-production"

    ALERT_THRESHOLDS: dict = {
        "MODERATE": 30,
        "HIGH": 55,
        "VERY_HIGH": 75,
        "CRITICAL": 90,
    }
    ALERT_COOLDOWN_MINUTES: int = 60

    HTTP_TIMEOUT_SECONDS: float = 8.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
