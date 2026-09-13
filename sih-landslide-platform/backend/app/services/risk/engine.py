from datetime import datetime, timezone

from core.config import get_settings
from schemas.common import Location
from schemas.risk import DataFreshnessEntry, RiskAssessment, RiskCategory
from services.historical.service import HistoricalEventService
from services.infrastructure.service import InfrastructureService
from services.risk.explainability import build_drivers
from services.risk.fusion import FeatureBundle, categorize, score
from services.risk.uncertainty import estimate_uncertainty
from services.satellite.service import SatelliteService
from services.terrain.demo_dem import get_terrain_features
from services.weather.service import WeatherService

# In-memory "previous assessment" cache for trend explanation. A real
# deployment persists this in risk_predictions (PostGIS) — see db/models.
_LAST_SCORE_CACHE: dict[str, float] = {}


class RiskEngine:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.weather = WeatherService()
        self.satellite = SatelliteService()
        self.historical = HistoricalEventService()

    async def assess(self, location: Location) -> RiskAssessment:
        now = datetime.now(timezone.utc)

        weather = await self.weather.get_weather(location)
        satellite = await self.satellite.get_change_summary(location)
        terrain = get_terrain_features(location)
        historical = self.historical.susceptibility_near(location)

        soil_moisture = None
        if weather.hourly:
            values = [h.soil_moisture_m3m3 for h in weather.hourly if h.soil_moisture_m3m3 is not None]
            if values:
                soil_moisture = sum(values) / len(values)

        bundle = FeatureBundle(
            rainfall_24h_mm=weather.rainfall_24h_mm,
            rainfall_72h_mm=weather.rainfall_72h_mm,
            precipitation_anomaly_pct=weather.precipitation_anomaly_pct,
            soil_moisture_m3m3=soil_moisture,
            slope_deg=terrain["slope_deg"],
            terrain_ruggedness_index=terrain["terrain_ruggedness_index"],
            ndvi_change=satellite.get("ndvi_change"),
            sar_change_score=satellite.get("sar_change_score"),
            historical_density=historical["historical_density"],
        )

        missing = sum(1 for v in bundle.__dict__.values() if v is None)
        result = score(bundle)
        drivers = build_drivers(result["contributions"], result["normalized_features"])
        uncertainty = estimate_uncertainty(
            result["normalized_features"], missing, len(bundle.__dict__),
            sum(result["contributions"].values()),
        )
        category = RiskCategory(categorize(result["risk_score"]))

        cache_key = f"{location.latitude:.3f},{location.longitude:.3f}"
        previous = _LAST_SCORE_CACHE.get(cache_key)
        trend_explanation = self._explain_trend(previous, result["risk_score"], drivers)
        _LAST_SCORE_CACHE[cache_key] = result["risk_score"]

        freshness = [
            DataFreshnessEntry(layer="weather", status=weather.envelope.status.value,
                                observed_at=weather.envelope.observed_at),
            DataFreshnessEntry(layer="satellite", status=satellite["envelope"].status.value,
                                observed_at=satellite["envelope"].observed_at),
            DataFreshnessEntry(layer="terrain", status="static"),
            DataFreshnessEntry(layer="historical", status="live" if historical["event_count"] else "seeded"),
        ]

        return RiskAssessment(
            location=location,
            risk_score=result["risk_score"],
            risk_probability=result["risk_probability"],
            category=category,
            confidence=uncertainty["confidence"],
            uncertainty=uncertainty["uncertainty"],
            timestamp=now,
            model_version=self.settings.MODEL_VERSION,
            feature_version=self.settings.FEATURE_VERSION,
            drivers=drivers,
            data_freshness=freshness,
            data_sources=[weather.envelope, satellite["envelope"]],
            previous_risk_score=previous,
            trend_explanation=trend_explanation,
        )

    @staticmethod
    def _explain_trend(previous: float | None, current: float, drivers: list) -> str | None:
        if previous is None:
            return None
        delta = current - previous
        if abs(delta) < 1:
            return "Risk score essentially unchanged since the previous assessment."
        top = drivers[0].factor if drivers else "the leading factor"
        direction = "increased" if delta > 0 else "decreased"
        return f"Risk {direction} by {abs(round(delta,1))} points, primarily driven by {top.lower()}."
