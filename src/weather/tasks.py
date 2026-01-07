import asyncio
from src.celery_app import celery_app
from src.weather.client import OpenWeatherClient
from src.weather.service import WeatherService
from src.weather.schemas import WeatherCreate
from src.database import async_session_maker
from src.config import settings
from src.utils import logger


async def fetch_and_save():
    """Async wrapper for the celery task logic."""
    client = OpenWeatherClient()

    async with async_session_maker() as session:
        for city in settings.CITIES_TO_TRACK:
            data = await client.get_weather(city)
            if data:
                schema = WeatherCreate(**data)
                await WeatherService.create_weather_record(session, schema)
            else:
                logger.warning(f"Skipping update for {city}")


@celery_app.task
def update_weather_data():
    """Periodic task to update weather data for all configured cities."""
    logger.info("Starting scheduled weather update...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fetch_and_save())
    logger.info("Weather update completed.")