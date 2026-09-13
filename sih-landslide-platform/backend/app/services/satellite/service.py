from app.core.config import get_settings
from app.schemas.common import DataStatus, Location
from app.services.satellite.demo_provider import build_demo_satellite_summary
from app.services.satellite.sentinel_hub_adapter import SentinelHubAdapter


class SatelliteService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.adapter = SentinelHubAdapter()

    async def get_change_summary(self, location: Location) -> dict:
        if self.settings.DEMO_MODE:
            return build_demo_satellite_summary(location)
        result = await self.adapter.find_latest_acquisition(location)
        if result["envelope"].status == DataStatus.UNAVAILABLE:
            demo = build_demo_satellite_summary(location)
            demo["envelope"].message = f"Live Sentinel Hub unavailable ({result['envelope'].message}); DEMO fallback shown."
            return demo
        # Real acquisition found: index computation would run here against
        # downloaded band arrays (see indices.py) — omitted pending credentials.
        return result

