from typing import Optional

from src.weather.dependencies import IWeatherRepository
from src.weather.entity import WeatherEntity
from src.weather.schemas import WeatherCreate, WeatherUpdate, WeatherResponse
from src.weather.client import OpenWeatherClient

from src.utils import logger


class WeatherService:
    """Service layer for weather business logic."""

    def __init__(self, repository: IWeatherRepository):
        self.repo = repository
        self.openweather_client = OpenWeatherClient()

    async def fetch_weather(self, city: str) -> Optional[WeatherResponse]:
        """Fetches the latest weather record for a city from OpenWeather API."""
        raw_weather_data = await self.openweather_client.get_weather(city)
        weather_entity = WeatherEntity(**raw_weather_data)

        city_instance = await self.repo.get_latest_weather(city)

        if city_instance is None:
            logger.error(f"City {city} not found.")
            return await self.repo.create_weather_record(weather_entity)

        weather_update_data = WeatherUpdate(
            temperature=weather_entity.temperature,
            pressure=weather_entity.pressure,
            humidity=weather_entity.humidity,
        )
        return await self.repo.update_weather_record(city_instance.id, weather_update_data)


    async def create_weather_record(self, data: WeatherCreate) -> WeatherResponse:
        """Creates a new weather record in the database."""
        entity = WeatherEntity(
            city=data.city,
            country=data.country,
            humidity=data.humidity,
            temperature=data.temperature,
            pressure=data.pressure,
        )
        return await self.repo.create_weather_record(entity)

    async def get_latest_weather(self, city: str) -> Optional[WeatherResponse]:
        """Retrieves latest weather from Database"""
        return await self.repo.get_latest_weather(city)

    async def update_weather_record(self, record_id: int, data: WeatherUpdate) -> Optional[WeatherResponse]:
        """Updates an existing weather record."""
        return await self.repo.update_weather_record(record_id, data)

    async def delete_weather_record(self, record_id: int) -> bool:
        """Deletes a weather record."""
        return await self.repo.delete_weather_record(record_id)
