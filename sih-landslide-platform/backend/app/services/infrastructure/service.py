from core.config import get_settings
from schemas.common import DataStatus, Location
from schemas.domain import InfrastructureResponse
from services.infrastructure.demo_provider import build_demo_infrastructure
from services.infrastructure.overpass_adapter import OverpassAdapter


class InfrastructureService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.adapter = OverpassAdapter()

    async def get_infrastructure(self, location: Location, radius_m: int = 5000) -> InfrastructureResponse:
        if self.settings.DEMO_MODE:
            return build_demo_infrastructure(location)
        result = await self.adapter.fetch_assets(location, radius_m)
        if result.envelope.status == DataStatus.UNAVAILABLE:
            demo = build_demo_infrastructure(location)
            demo.envelope.message = f"Live OSM source unavailable; showing DEMO fallback."
            return demo
        return result
