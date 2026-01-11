import httpx
from src.config import settings
from src.utils import logger
from src.weather.schemas import WeatherCreate


class OpenWeatherClient:
    """
    Client for interacting with the OpenWeatherMap API.
    """

    def __init__(self, api_key: str = settings.WEATHER_API_KEY, base_url: str = settings.WEATHER_API_URL):
        """
        Initializes the OpenWeatherClient.

        Args:
            api_key (str): API key for OpenWeatherMap. Defaults to settings.WEATHER_API_KEY.
            base_url (str): Base URL for the API. Defaults to settings.WEATHER_API_URL.
        """
        self.api_key = api_key
        self.base_url = base_url

    async def get_weather(self, city: str) -> WeatherCreate | None:
        """
        Fetches current weather for a specific city.

        Args:
            city (str): Name of the city to fetch weather for.

        Returns:
            WeatherCreate | None: Parsed weather data as a Pydantic model, or None if the request fails (e.g., city not found or API error).
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

                logger.info("Successfully fetched weather data", city=city)

                return WeatherCreate(
                    city=data["name"],
                    country=data["sys"]["country"],
                    temperature=data["main"]["temp"],
                    humidity=data["main"]["humidity"],
                    pressure=data["main"]["pressure"]
                )
            except httpx.HTTPError as e:
                logger.error("Failed to fetch weather data", city=city, error=str(e))
                return None
            except KeyError as e:
                logger.error("Invalid response structure from OpenWeather API", city=city, error=str(e))
                return None