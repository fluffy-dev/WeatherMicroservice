from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.weather.models import WeatherData
from src.weather.schemas import WeatherCreate, WeatherUpdate
from src.utils import logger


class WeatherService:
    """Service layer for weather business logic."""

    @staticmethod
    async def create_weather_record(session: AsyncSession, data: WeatherCreate) -> WeatherData:
        """Creates a new weather record in the database.

        Args:
            session: Database session.
            data: Weather data schema.

        Returns:
            WeatherData: Created database instance.
        """

        new_record = WeatherData(**data.model_dump())
        session.add(new_record)
        await session.commit()
        await session.refresh(new_record)
        logger.info(f"Recorded weather for {new_record.city}")
        return new_record

    @staticmethod
    async def get_latest_weather(session: AsyncSession, city: str) -> WeatherData | None:
        """Retrieves the latest weather record for a city.

        Args:
            session: Database session.
            city: City name.

        Returns:
            WeatherData | None: The latest record or None.
        """
        query = (
            select(WeatherData)
            .where(WeatherData.city == city)
            .order_by(WeatherData.fetched_at.desc())
            .limit(1)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_weather_record(
            session: AsyncSession,
            record_id: int,
            data: WeatherUpdate
    ) -> WeatherData | None:
        """Updates an existing weather record.

        Args:
            session: Database session.
            record_id: ID of the record.
            data: Data to update.

        Returns:
            WeatherData | None: Updated record or None if not found.
        """
        query = (
            update(WeatherData)
            .where(WeatherData.id == record_id)
            .values(**data.model_dump(exclude_unset=True))
            .returning(WeatherData)
        )
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_weather_record(session: AsyncSession, record_id: int) -> bool:
        """Deletes a weather record.

        Args:
            session: Database session.
            record_id: ID of the record.

        Returns:
            bool: True if deleted, False otherwise.
        """
        query = delete(WeatherData).where(WeatherData.id == record_id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0