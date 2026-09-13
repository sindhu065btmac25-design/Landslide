from fastapi import APIRouter, Query

from schemas.common import Location
from schemas.domain import InfrastructureResponse
from services.infrastructure.service import InfrastructureService

router = APIRouter(prefix="/api/v1/infrastructure", tags=["infrastructure"])
service = InfrastructureService()


@router.get("", response_model=InfrastructureResponse)
async def infrastructure(lat: float = Query(...), lon: float = Query(...), radius_m: int = 5000):
    return await service.get_infrastructure(Location(latitude=lat, longitude=lon), radius_m)
