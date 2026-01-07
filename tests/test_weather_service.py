import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.weather.service import WeatherService
from src.weather.schemas import WeatherCreate, WeatherUpdate


@pytest.mark.asyncio
async def test_create_and_get_weather(db_session: AsyncSession):
    """Test creating a record and retrieving the latest one."""
    weather_data = WeatherCreate(
        city="ServiceCity",
        country="SC",
        temperature=10.5,
        humidity=50,
        pressure=1000
    )

    # 1. Create
    created = await WeatherService.create_weather_record(db_session, weather_data)
    assert created.id is not None
    assert created.city == "ServiceCity"

    # 2. Get Latest
    fetched = await WeatherService.get_latest_weather(db_session, "ServiceCity")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.temperature == 10.5


@pytest.mark.asyncio
async def test_get_latest_weather_ordering(db_session: AsyncSession):
    """Test that get_latest_weather returns the most recent record."""
    city_name = "TimeCity"

    # Create older record
    data1 = WeatherCreate(
        city=city_name, country="TC", temperature=10.0, humidity=50, pressure=1000
    )
    await WeatherService.create_weather_record(db_session, data1)

    # Create newer record
    data2 = WeatherCreate(
        city=city_name, country="TC", temperature=20.0, humidity=60, pressure=1005
    )
    await WeatherService.create_weather_record(db_session, data2)

    # Fetch
    latest = await WeatherService.get_latest_weather(db_session, city_name)
    assert latest is not None
    # Should be the second one (higher temp)
    assert latest.temperature == 20.0


@pytest.mark.asyncio
async def test_update_weather(db_session: AsyncSession):
    """Test updating an existing record."""
    # Create initial
    data = WeatherCreate(
        city="UpdateCity", country="UC", temperature=0.0, humidity=0, pressure=1000
    )
    created = await WeatherService.create_weather_record(db_session, data)

    # Update
    update_data = WeatherUpdate(temperature=25.5, humidity=80)
    updated = await WeatherService.update_weather_record(db_session, created.id, update_data)

    assert updated is not None
    assert updated.temperature == 25.5
    assert updated.humidity == 80
    assert updated.pressure == 1000  # Should remain unchanged


@pytest.mark.asyncio
async def test_delete_weather(db_session: AsyncSession):
    """Test deleting a record."""
    data = WeatherCreate(
        city="DeleteCity", country="DC", temperature=0.0, humidity=0, pressure=1000
    )
    created = await WeatherService.create_weather_record(db_session, data)

    # Delete
    success = await WeatherService.delete_weather_record(db_session, created.id)
    assert success is True

    # Verify deletion
    fetched = await WeatherService.get_latest_weather(db_session, "DeleteCity")
    assert fetched is None