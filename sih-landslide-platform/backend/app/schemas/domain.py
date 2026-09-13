from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.schemas.common import Location, SourceEnvelope
from app.schemas.risk import RiskCategory


class AssetType(str, Enum):
    ROAD = "road"
    BRIDGE = "bridge"
    SETTLEMENT = "settlement"
    HOSPITAL = "hospital"
    SCHOOL = "school"


class InfrastructureAsset(BaseModel):
    id: str
    type: AssetType
    name: str | None = None
    latitude: float
    longitude: float
    estimated_population: int | None = None


class InfrastructureResponse(BaseModel):
    envelope: SourceEnvelope
    assets: list[InfrastructureAsset]


class ImpactSummary(BaseModel):
    location: Location
    risk_category: RiskCategory
    affected_roads_km: float
    affected_bridges: int
    affected_settlements: int
    estimated_population_exposure: int
    ranked_assets: list[InfrastructureAsset]


class DecisionRecommendation(BaseModel):
    risk_category: RiskCategory
    actions: list[str]
    note: str = "Decision-support suggestion only — not an autonomous order."


class AlertSeverity(str, Enum):
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    CRITICAL = "CRITICAL"


class Alert(BaseModel):
    id: str
    severity: AlertSeverity
    location: Location
    previous_category: RiskCategory | None = None
    new_category: RiskCategory
    reasons: list[str]
    affected_assets: list[str]
    recommended_actions: list[str]
    created_at: datetime


class FeedbackType(str, Enum):
    LANDSLIDE_CONFIRMED = "landslide_confirmed"
    FALSE_ALARM = "false_alarm"
    NO_LANDSLIDE = "no_landslide"
    SEVERITY_INCORRECT = "severity_incorrect"
    ASSET_CONFIRMED = "asset_confirmed"
    ASSET_INCORRECT = "asset_incorrect"


class FeedbackSubmission(BaseModel):
    location: Location
    feedback_type: FeedbackType
    related_risk_assessment_id: str | None = None
    notes: str | None = None
    submitted_by: str | None = None


class FeedbackRecord(FeedbackSubmission):
    id: str
    created_at: datetime

