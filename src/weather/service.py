from typing import Optional

from src.weather.dependencies import IWeatherRepository
from src.weather.entity import WeatherEntity
from src.weather.schemas import WeatherCreate, WeatherUpdate, WeatherResponse
from src.weather.client import OpenWeatherClient
from src.weather.exceptions import WeatherNotFound
from src.utils import logger


class WeatherService:
    """
    Service layer for weather business logic.
    """

    def __init__(self, repository: IWeatherRepository):
        """
        Initializes the WeatherService.

        Args:
            repository (IWeatherRepository): The weather repository.
        """
        self.repo = repository
        self.openweather_client = OpenWeatherClient()

    async def fetch_weather(self, city: str) -> WeatherResponse:
        """
        Fetches the latest weather record for a city.
        First attempts to fetch from OpenWeatherMap API and save to DB.
        If that fails/returns None, falls back to the database.

        Args:
            city (str): The name of the city.

        Returns:
            WeatherResponse: The weather data.

        Raises:
            WeatherNotFound: If weather data cannot be found in both API and DB.
        """
        # Try fetching from external API
        external_weather = await self.openweather_client.get_weather(city)
        
        if external_weather:
            # Save new data
            entity = WeatherEntity(
                city=external_weather.city,
                country=external_weather.country,
                humidity=external_weather.humidity,
                temperature=external_weather.temperature,
                pressure=external_weather.pressure,
            )
            return await self.repo.create_weather_record(entity)
        
        # Fallback to DB if external API fails or returns nothing
        try:
            return await self.repo.get_latest_weather(city)
        except WeatherNotFound:
            # If not in DB either, re-raise because we really didn't find it anywhere
            logger.error("Weather data not found in both external API and database", city=city)
            raise

    async def create_weather_record(self, data: WeatherCreate) -> WeatherResponse:
        """
        Creates a new weather record manually.

        Args:
            data (WeatherCreate): The weather data to create.

        Returns:
            WeatherResponse: The created weather record.
        """
        entity = WeatherEntity(
            city=data.city,
            country=data.country,
            humidity=data.humidity,
            temperature=data.temperature,
            pressure=data.pressure,
        )
        return await self.repo.create_weather_record(entity)

    async def get_latest_weather(self, city: str) -> WeatherResponse:
        """
        Retrieves the latest weather record for a city from the database.

        Args:
            city (str): The city name.

        Returns:
            WeatherResponse: The weather record.

        Raises:
            WeatherNotFound: If the record is not found.
        """
        return await self.repo.get_latest_weather(city)

    async def update_weather_record(self, record_id: int, data: WeatherUpdate) -> WeatherResponse:
        """
        Updates an existing weather record.

        Args:
            record_id (int): The ID of the record.
            data (WeatherUpdate): The data to update.

        Returns:
            WeatherResponse: The updated record.

        Raises:
            WeatherNotFound: If the record is not found.
        """
        return await self.repo.update_weather_record(record_id, data)

    async def delete_weather_record(self, record_id: int) -> None:
        """
        Deletes a weather record.

        Args:
            record_id (int): The ID of the record.

        Raises:
            WeatherNotFound: If the record is not found.
        """
        await self.repo.delete_weather_record(record_id)
