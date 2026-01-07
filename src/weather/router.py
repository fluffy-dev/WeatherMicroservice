from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.weather.schemas import WeatherCreate, WeatherResponse, WeatherUpdate
from src.weather.service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.post("/", response_model=WeatherResponse, status_code=status.HTTP_201_CREATED)
async def create_weather(
    weather: WeatherCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new manual weather entry."""
    return await WeatherService.create_weather_record(session, weather)


@router.get("/{city}", response_model=WeatherResponse)
async def get_weather(
        city: str,
        session: AsyncSession = Depends(get_async_session)
):
    result = await WeatherService.get_latest_weather(session, city)
    if result:
        return result

    client = OpenWeatherClient()
    external_data = await client.get_weather(city)

    if not external_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City '{city}' not found in database or external API"
        )

    weather_schema = WeatherCreate(**external_data)
    new_record = await WeatherService.create_weather_record(session, weather_schema)

    return new_record


@router.patch("/{record_id}", response_model=WeatherResponse)
async def update_weather(
    record_id: int,
    weather: WeatherUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Update a specific weather record."""
    result = await WeatherService.update_weather_record(session, record_id, weather)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return result


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weather(
    record_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a weather record."""
    deleted = await WeatherService.delete_weather_record(session, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")