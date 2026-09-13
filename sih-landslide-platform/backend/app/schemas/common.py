from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DataStatus(str, Enum):
    LIVE = "live"
    DEMO = "demo"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class Location(BaseModel):
    latitude: float
    longitude: float
    name: str | None = None
    state: str | None = None
    district: str | None = None


class SourceEnvelope(BaseModel):
    """Every external-data response is wrapped in this envelope so the
    frontend can render LIVE / DEMO / DEGRADED / OFFLINE truthfully."""

    status: DataStatus
    source: str
    observed_at: datetime | None = None
    ingested_at: datetime
    age_seconds: float | None = None
    message: str | None = None

