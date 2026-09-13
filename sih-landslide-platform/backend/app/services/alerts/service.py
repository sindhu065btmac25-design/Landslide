"""Alerting: threshold-crossing detection with cooldown + dedup, per §18.
In-memory state here; production build persists to the `alerts` table."""
import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.schemas.common import Location
from app.schemas.domain import Alert, AlertSeverity
from app.schemas.risk import RiskCategory

_STATE: dict[str, dict] = {}  # cache_key -> {"category": ..., "last_alert_at": ...}

CATEGORY_ORDER = [RiskCategory.LOW, RiskCategory.MODERATE, RiskCategory.HIGH,
                   RiskCategory.VERY_HIGH, RiskCategory.CRITICAL]


class AlertService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def evaluate(self, location: Location, new_category: RiskCategory, drivers: list,
                 affected_assets: list[str], recommended_actions: list[str]) -> Alert | None:
        key = f"{location.latitude:.3f},{location.longitude:.3f}"
        now = datetime.now(timezone.utc)
        state = _STATE.get(key)
        previous_category = state["category"] if state else None

        crossed_up = (
            previous_category is None
            or CATEGORY_ORDER.index(new_category) > CATEGORY_ORDER.index(previous_category)
        )
        in_cooldown = (
            state and now - state["last_alert_at"] < timedelta(minutes=self.settings.ALERT_COOLDOWN_MINUTES)
        )
        is_alertable = new_category in (RiskCategory.MODERATE, RiskCategory.HIGH,
                                          RiskCategory.VERY_HIGH, RiskCategory.CRITICAL)

        _STATE[key] = {"category": new_category, "last_alert_at": state["last_alert_at"] if (state and in_cooldown) else now}

        if not (crossed_up and is_alertable) or in_cooldown:
            return None

        return Alert(
            id=uuid.uuid4().hex,
            severity=AlertSeverity(new_category.value),
            location=location,
            previous_category=previous_category,
            new_category=new_category,
            reasons=[f"{d.factor} (contribution {d.contribution:.0%})" for d in drivers[:3]],
            affected_assets=affected_assets,
            recommended_actions=recommended_actions,
            created_at=now,
        )

