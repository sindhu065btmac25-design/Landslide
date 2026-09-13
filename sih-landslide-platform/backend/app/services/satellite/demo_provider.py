"""Deterministic demo satellite summary — used when Sentinel Hub adapter
reports UNAVAILABLE. Clearly labeled DEMO, never framed as a real acquisition."""
import hashlib
from datetime import datetime, timedelta, timezone

from schemas.common import DataStatus, Location, SourceEnvelope


def _seed(location: Location, salt: str) -> float:
    key = f"{location.latitude:.3f}:{location.longitude:.3f}:{salt}"
    digest = hashlib.sha256(key.encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def build_demo_satellite_summary(location: Location) -> dict:
    now = datetime.now(timezone.utc)
    days_ago = int(2 + _seed(location, "age") * 6)
    observed_at = now - timedelta(days=days_ago)
    ndvi_change = round(_seed(location, "ndvi") * 0.4, 3)
    sar_change = round(_seed(location, "sar") * 0.5, 3)
    return {
        "envelope": SourceEnvelope(
            status=DataStatus.DEMO, source="demo-satellite-generator",
            observed_at=observed_at, ingested_at=now,
            message="DEMO MODE — synthetic change indices, not a real acquisition.",
        ),
        "ndvi_change": ndvi_change,
        "vegetation_loss_pct": round(ndvi_change * 100, 1),
        "sar_change_score": sar_change,
        "cloud_cover_pct": round(_seed(location, "cloud") * 40, 1),
    }
