from fastapi import APIRouter, status

from src.weather.dependencies import IWeatherService
from src.weather.schemas import WeatherCreate, WeatherResponse, WeatherUpdate

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.post("/", response_model=WeatherResponse, status_code=status.HTTP_201_CREATED)
async def create_weather(
    weather: WeatherCreate,
    service: IWeatherService
):
    """
    Creates a new manual weather entry.

    Args:
        weather (WeatherCreate): The weather data to create.
        service (IWeatherService): The weather service.

    Returns:
        WeatherResponse: The created weather record.
    """
    return await service.create_weather_record(weather)


@router.get("/{city}", response_model=WeatherResponse)
async def get_weather(
        city: str,
        service: IWeatherService
):
    """
    Retrieves weather data for a specific city.
    Connects to external API if data is not available or outdated (logic inside service).

    Args:
        city (str): The name of the city.
        service (IWeatherService): The weather service.

    Returns:
        WeatherResponse: The weather data.
    """
    return await service.fetch_weather(city)


@router.patch("/{record_id}", response_model=WeatherResponse)
async def update_weather(
    record_id: int,
    weather: WeatherUpdate,
    service: IWeatherService
):
    """
    Updates a specific weather record.

    Args:
        record_id (int): The ID of the record to update.
        weather (WeatherUpdate): The data to update.
        service (IWeatherService): The weather service.

    Returns:
        WeatherResponse: The updated weather record.
    """
    return await service.update_weather_record(record_id, weather)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weather(
    record_id: int,
    service: IWeatherService
):
    """
    Deletes a weather record.

    Args:
        record_id (int): The ID of the record to delete.
        service (IWeatherService): The weather service.
    """
    await service.delete_weather_record(record_id)