from fastapi import APIRouter, Query

from schemas.common import Location
from services.alerts.service import AlertService
from services.decision.service import DecisionService
from services.impact.service import ImpactService
from services.infrastructure.service import InfrastructureService
from services.risk.engine import RiskEngine

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])
engine = RiskEngine()
infra_service = InfrastructureService()
impact_service = ImpactService()
decision_service = DecisionService()
alert_service = AlertService()


@router.get("")
async def check_alert(lat: float = Query(...), lon: float = Query(...)):
    location = Location(latitude=lat, longitude=lon)
    assessment = await engine.assess(location)
    infra = await infra_service.get_infrastructure(location)
    impact = impact_service.assess_impact(location, assessment.category, infra.assets)
    decision = decision_service.recommend(assessment.category, assessment.uncertainty, impact.estimated_population_exposure)

    alert = alert_service.evaluate(
        location, assessment.category, assessment.drivers,
        [a.name or a.id for a in impact.ranked_assets], decision.actions,
    )
    return {"alert": alert, "assessment_category": assessment.category}
