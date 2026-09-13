import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

import pytest

from schemas.common import Location
from services.risk.engine import RiskEngine
from services.risk.fusion import FeatureBundle, categorize, score


def test_fusion_score_is_deterministic_and_bounded():
    bundle = FeatureBundle(
        rainfall_24h_mm=80, rainfall_72h_mm=150, precipitation_anomaly_pct=20,
        soil_moisture_m3m3=0.3, slope_deg=35, terrain_ruggedness_index=6,
        ndvi_change=0.2, sar_change_score=0.25, historical_density=0.5,
    )
    result_a = score(bundle)
    result_b = score(bundle)
    assert result_a == result_b
    assert 0 <= result_a["risk_score"] <= 100
    assert 0 <= result_a["risk_probability"] <= 1


def test_categorize_thresholds():
    assert categorize(10) == "LOW"
    assert categorize(40) == "MODERATE"
    assert categorize(60) == "HIGH"
    assert categorize(80) == "VERY_HIGH"
    assert categorize(95) == "CRITICAL"


def test_high_rainfall_and_slope_increase_risk():
    low = FeatureBundle(5, 10, 0, 0.1, 5, 1, 0, 0, 0)
    high = FeatureBundle(140, 280, 40, 0.4, 44, 9, 0.35, 0.45, 0.9)
    assert score(high)["risk_score"] > score(low)["risk_score"]


@pytest.mark.asyncio
async def test_risk_engine_assess_runs_in_demo_mode():
    engine = RiskEngine()
    assessment = await engine.assess(Location(latitude=26.14, longitude=91.73, name="Guwahati"))
    assert 0 <= assessment.risk_score <= 100
    assert assessment.category is not None
    assert len(assessment.drivers) > 0
    assert assessment.model_version
