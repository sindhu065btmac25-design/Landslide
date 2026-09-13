from fastapi import APIRouter, Query

from schemas.common import Location
from services.terrain.demo_dem import get_terrain_features

router = APIRouter(prefix="/api/v1/terrain", tags=["terrain"])


@router.get("")
async def terrain(lat: float = Query(...), lon: float = Query(...)):
    return get_terrain_features(Location(latitude=lat, longitude=lon))
