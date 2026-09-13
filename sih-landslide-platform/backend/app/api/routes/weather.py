from fastapi import APIRouter, Query

from app.schemas.common import Location
from app.schemas.weather import WeatherResponse
from app.services.weather.service import WeatherService

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])
service = WeatherService()


@router.get("/current", response_model=WeatherResponse)
async def current(lat: float = Query(...), lon: float = Query(...), name: str | None = None):
    return await service.get_weather(Location(latitude=lat, longitude=lon, name=name))


@router.get("/forecast", response_model=WeatherResponse)
async def forecast(lat: float = Query(...), lon: float = Query(...), name: str | None = None):
    return await service.get_weather(Location(latitude=lat, longitude=lon, name=name))

