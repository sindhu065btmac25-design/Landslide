from fastapi import APIRouter, Query

from app.schemas.common import Location
from app.services.risk.engine import RiskEngine

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
engine = RiskEngine()


@router.get("/timeseries")
async def timeseries(lat: float = Query(...), lon: float = Query(...)):
    """Single current point plus trend explanation; a production build reads
    the risk_predictions history table for a real multi-point series."""
    assessment = await engine.assess(Location(latitude=lat, longitude=lon))
    return {
        "current": {"risk_score": assessment.risk_score, "timestamp": assessment.timestamp},
        "previous_risk_score": assessment.previous_risk_score,
        "trend_explanation": assessment.trend_explanation,
        "note": "Full historical series requires the persisted risk_predictions table (PostGIS), not populated in this scaffold run.",
    }

