from fastapi import APIRouter, Query

from schemas.common import Location
from schemas.risk import RiskAssessment
from services.risk.engine import RiskEngine

router = APIRouter(prefix="/api/v1/risk", tags=["risk"])
engine = RiskEngine()

# NER bounding approximation for a coarse demo grid.
NER_BBOX = {"lat_min": 22.0, "lat_max": 29.5, "lon_min": 88.0, "lon_max": 97.5}


@router.get("/location/{lat}/{lon}", response_model=RiskAssessment)
async def risk_at_location(lat: float, lon: float, name: str | None = None):
    return await engine.assess(Location(latitude=lat, longitude=lon, name=name))


@router.get("/summary")
async def risk_summary(lat: float = Query(...), lon: float = Query(...)):
    assessment = await engine.assess(Location(latitude=lat, longitude=lon))
    return {
        "risk_score": assessment.risk_score,
        "category": assessment.category,
        "confidence": assessment.confidence,
        "uncertainty": assessment.uncertainty,
        "timestamp": assessment.timestamp,
    }


@router.get("/grid")
async def risk_grid(state: str | None = None, cell_deg: float = 1.0, sample_limit: int = 9):
    """Coarse demo risk grid over the NER bbox (or a state's approximate
    center if provided). A production build serves this from cached
    risk_grid_cells in PostGIS rather than computing on request."""
    import math

    lat_steps = max(1, int((NER_BBOX["lat_max"] - NER_BBOX["lat_min"]) / cell_deg))
    lon_steps = max(1, int((NER_BBOX["lon_max"] - NER_BBOX["lon_min"]) / cell_deg))
    points = []
    for i in range(lat_steps):
        for j in range(lon_steps):
            lat = NER_BBOX["lat_min"] + i * cell_deg
            lon = NER_BBOX["lon_min"] + j * cell_deg
            points.append((lat, lon))
    points = points[:sample_limit]

    results = []
    for lat, lon in points:
        assessment = await engine.assess(Location(latitude=lat, longitude=lon))
        results.append({
            "latitude": lat, "longitude": lon,
            "risk_score": assessment.risk_score, "category": assessment.category,
        })
    return {"cells": results, "note": "Coarse sampled demo grid — production uses cached PostGIS risk_grid_cells."}
