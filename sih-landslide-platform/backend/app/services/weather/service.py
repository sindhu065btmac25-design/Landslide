from core.config import get_settings
from schemas.common import DataStatus, Location
from schemas.weather import WeatherResponse
from services.weather.demo_provider import build_demo_weather
from services.weather.open_meteo_adapter import OpenMeteoAdapter


class WeatherService:
    """Facade: tries the live adapter unless DEMO_MODE is forced; falls back
    to the labeled demo provider if the live call is unavailable."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.adapter = OpenMeteoAdapter()

    async def get_weather(self, location: Location) -> WeatherResponse:
        if self.settings.DEMO_MODE:
            return build_demo_weather(location)

        result = await self.adapter.fetch_current_and_forecast(location)
        if result.envelope.status == DataStatus.UNAVAILABLE:
            demo = build_demo_weather(location)
            demo.envelope.message = (
                f"Live source unavailable ({result.envelope.message}); "
                "showing DEMO fallback — this is NOT a live observation."
            )
            return demo
        return result
