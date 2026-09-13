from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.schemas.common import Location, SourceEnvelope


class RiskCategory(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    CRITICAL = "CRITICAL"


class RiskDriver(BaseModel):
    factor: str
    contribution: float  # signed, sums (abs) roughly to 1.0 across drivers
    value: float | None = None
    description: str | None = None


class DataFreshnessEntry(BaseModel):
    layer: str
    status: str
    observed_at: datetime | None = None
    age_minutes: float | None = None


class RiskAssessment(BaseModel):
    location: Location
    risk_score: float  # 0-100
    risk_probability: float  # 0-1
    category: RiskCategory
    confidence: float  # 0-1, how much we trust this number
    uncertainty: float  # 0-1, +/- band on risk_probability
    timestamp: datetime
    model_version: str
    feature_version: str
    drivers: list[RiskDriver]
    data_freshness: list[DataFreshnessEntry]
    data_sources: list[SourceEnvelope]
    previous_risk_score: float | None = None
    trend_explanation: str | None = None

