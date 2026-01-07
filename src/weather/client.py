import httpx
from src.config import settings
from src.utils import logger


class OpenWeatherClient:
    """Client for interacting with OpenWeatherMap API."""

    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_URL

    async def get_weather(self, city: str) -> dict | None:
        """Fetches current weather for a specific city.

        Args:
            city: Name of the city.

        Returns:
            dict | None: Parsed weather data or None if request failed.
        """
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/weather", params=params)
                response.raise_for_status()
                data = response.json()

                return {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"]
                }
            except httpx.HTTPError as e:
                logger.error(f"Failed to fetch weather for {city}: {e}")
                return None