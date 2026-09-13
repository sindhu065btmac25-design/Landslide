from fastapi import APIRouter, Query

from app.schemas.common import Location
from app.services.satellite.service import SatelliteService

router = APIRouter(prefix="/api/v1/satellite", tags=["satellite"])
service = SatelliteService()


@router.get("/latest")
async def latest(lat: float = Query(...), lon: float = Query(...)):
    return await service.get_change_summary(Location(latitude=lat, longitude=lon))


@router.get("/change")
async def change(lat: float = Query(...), lon: float = Query(...)):
    return await service.get_change_summary(Location(latitude=lat, longitude=lon))

