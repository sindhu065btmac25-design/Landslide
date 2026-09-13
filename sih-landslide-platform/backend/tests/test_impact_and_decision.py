import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from schemas.common import Location
from schemas.domain import AssetType, InfrastructureAsset
from schemas.risk import RiskCategory
from services.decision.service import DecisionService
from services.impact.service import ImpactService


def test_impact_filters_by_radius():
    loc = Location(latitude=26.0, longitude=91.0)
    near = InfrastructureAsset(id="near", type=AssetType.SETTLEMENT, latitude=26.001, longitude=91.001, estimated_population=100)
    far = InfrastructureAsset(id="far", type=AssetType.SETTLEMENT, latitude=27.5, longitude=93.0, estimated_population=100)
    summary = ImpactService().assess_impact(loc, RiskCategory.HIGH, [near, far])
    ids = [a.id for a in summary.ranked_assets]
    assert "near" in ids
    assert "far" not in ids


def test_decision_engine_escalates_for_high_uncertainty():
    rec = DecisionService().recommend(RiskCategory.HIGH, uncertainty=0.7, population_exposure=200)
    assert any("uncertainty" in a.lower() for a in rec.actions)


def test_decision_engine_escalates_for_population():
    rec = DecisionService().recommend(RiskCategory.VERY_HIGH, uncertainty=0.1, population_exposure=5000)
    assert any("escalate" in a.lower() for a in rec.actions)
