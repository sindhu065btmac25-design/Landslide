"""Deterministic demo infrastructure set around a point, used when Overpass
is unreachable (no network) or DEMO_MODE is forced."""
import hashlib
from datetime import datetime, timezone

from app.schemas.common import DataStatus, Location, SourceEnvelope
from app.schemas.domain import AssetType, InfrastructureAsset, InfrastructureResponse


def _offset(location: Location, salt: str, scale: float) -> float:
    key = f"{location.latitude:.3f}:{location.longitude:.3f}:{salt}"
    digest = hashlib.sha256(key.encode()).hexdigest()
    val = (int(digest[:8], 16) / 0xFFFFFFFF) - 0.5
    return val * scale


def build_demo_infrastructure(location: Location) -> InfrastructureResponse:
    now = datetime.now(timezone.utc)
    assets = [
        InfrastructureAsset(
            id="demo-road-1", type=AssetType.ROAD, name="NH-Demo Highway",
            latitude=location.latitude + _offset(location, "r1", 0.03),
            longitude=location.longitude + _offset(location, "r1b", 0.03),
        ),
        InfrastructureAsset(
            id="demo-bridge-1", type=AssetType.BRIDGE, name="Demo River Bridge",
            latitude=location.latitude + _offset(location, "b1", 0.02),
            longitude=location.longitude + _offset(location, "b1b", 0.02),
        ),
        InfrastructureAsset(
            id="demo-settlement-1", type=AssetType.SETTLEMENT, name="Demo Village",
            latitude=location.latitude + _offset(location, "s1", 0.015),
            longitude=location.longitude + _offset(location, "s1b", 0.015),
            estimated_population=850,
        ),
        InfrastructureAsset(
            id="demo-hospital-1", type=AssetType.HOSPITAL, name="Demo Community Health Centre",
            latitude=location.latitude + _offset(location, "h1", 0.025),
            longitude=location.longitude + _offset(location, "h1b", 0.025),
        ),
        InfrastructureAsset(
            id="demo-school-1", type=AssetType.SCHOOL, name="Demo Govt. School",
            latitude=location.latitude + _offset(location, "sc1", 0.018),
            longitude=location.longitude + _offset(location, "sc1b", 0.018),
        ),
    ]
    envelope = SourceEnvelope(
        status=DataStatus.DEMO, source="demo-infrastructure-generator", observed_at=now,
        ingested_at=now, message="DEMO MODE — synthetic assets, not real OSM data.",
    )
    return InfrastructureResponse(envelope=envelope, assets=assets)

