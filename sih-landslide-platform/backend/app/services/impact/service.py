"""Impact engine: real haversine-distance-based intersection of a risk
location with nearby infrastructure assets. A production build would use
PostGIS ST_DWithin/ST_Intersects over risk polygons; this uses a radius
proxy so it works without a live PostGIS instance in this scaffold."""
import math

from app.schemas.common import Location
from app.schemas.domain import AssetType, ImpactSummary, InfrastructureAsset
from app.schemas.risk import RiskCategory


def _haversine_km(a_lat, a_lon, b_lat, b_lon) -> float:
    r = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dlambda = math.radians(b_lon - a_lon)
    x = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(x))


SEVERITY_RADIUS_KM = {
    RiskCategory.LOW: 1.0, RiskCategory.MODERATE: 2.0, RiskCategory.HIGH: 4.0,
    RiskCategory.VERY_HIGH: 6.0, RiskCategory.CRITICAL: 9.0,
}


class ImpactService:
    def assess_impact(self, location: Location, risk_category: RiskCategory,
                       assets: list[InfrastructureAsset]) -> ImpactSummary:
        radius = SEVERITY_RADIUS_KM.get(risk_category, 2.0)
        affected = [a for a in assets if _haversine_km(location.latitude, location.longitude,
                                                         a.latitude, a.longitude) <= radius]
        affected.sort(key=lambda a: _haversine_km(location.latitude, location.longitude, a.latitude, a.longitude))

        roads_km = sum(0.8 for a in affected if a.type == AssetType.ROAD)  # proxy: avg segment length
        bridges = sum(1 for a in affected if a.type == AssetType.BRIDGE)
        settlements = sum(1 for a in affected if a.type == AssetType.SETTLEMENT)
        population = sum(a.estimated_population or (250 if a.type == AssetType.SETTLEMENT else 0) for a in affected)

        return ImpactSummary(
            location=location, risk_category=risk_category,
            affected_roads_km=round(roads_km, 1), affected_bridges=bridges,
            affected_settlements=settlements, estimated_population_exposure=population,
            ranked_assets=affected,
        )

