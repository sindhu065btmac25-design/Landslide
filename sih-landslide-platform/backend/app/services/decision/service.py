"""Decision engine: rule table straight from spec §14. Recommendations are
decision-support suggestions, never autonomous orders."""
from app.schemas.domain import DecisionRecommendation
from app.schemas.risk import RiskCategory

ACTIONS = {
    RiskCategory.LOW: ["Continue routine monitoring"],
    RiskCategory.MODERATE: ["Increase monitoring frequency", "Inspect vulnerable slopes"],
    RiskCategory.HIGH: ["Schedule field inspection", "Prepare emergency response resources",
                          "Notify district disaster authorities"],
    RiskCategory.VERY_HIGH: ["Conduct immediate field inspection", "Pre-position evacuation resources",
                               "Evaluate traffic restrictions on nearby roads"],
    RiskCategory.CRITICAL: ["Initiate emergency coordination", "Evaluate evacuation of nearby settlements",
                              "Evaluate road closure / traffic restriction"],
}


class DecisionService:
    def recommend(self, risk_category: RiskCategory, uncertainty: float, population_exposure: int) -> DecisionRecommendation:
        actions = list(ACTIONS.get(risk_category, ACTIONS[RiskCategory.LOW]))
        if uncertainty > 0.5:
            actions.append("Uncertainty is high — prioritize field verification before acting on this score alone")
        if population_exposure > 1000 and risk_category in (RiskCategory.HIGH, RiskCategory.VERY_HIGH, RiskCategory.CRITICAL):
            actions.append(f"~{population_exposure} people estimated in the exposure zone — escalate priority")
        return DecisionRecommendation(risk_category=risk_category, actions=actions)

