from typing import Optional

from sqlalchemy import select, delete, update
from src.weather.models import WeatherData
from src.weather.schemas import WeatherUpdate, WeatherResponse
from src.weather.entity import WeatherEntity

from src.database import ISession


class WeatherRepository:
    """Service layer for weather business logic."""

    def __init__(self, session: ISession):
        self.session = session

    async def create_weather_record(self, data: WeatherEntity) -> WeatherResponse:
        """Creates a new weather record in the database.

        Args:
            data: Weather data schema.

        Returns:
            WeatherData: Created database instance.
        """

        new_record = WeatherData(
            city=data.city,
            country=data.country,
            temperature=data.temperature,
            humidity=data.humidity,
            pressure=data.pressure
            )
        self.session.add(new_record)
        await self.session.commit()
        await self.session.refresh(new_record)
        return self._to_dto(new_record)

    async def get_latest_weather(self, city: str) -> Optional[WeatherResponse]:
        """Retrieves the latest weather record for a city.

        Args:
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
        raw = await self.session.execute(query)
        result = raw.scalar_one_or_none()
        return self._to_dto(result) if raw else None


    async def update_weather_record(
            self,
            record_id: int,
            data: WeatherUpdate
    ) -> Optional[WeatherResponse]:
        """Updates an existing weather record.

        Args:
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
        raw = await self.session.execute(query)
        await self.session.commit()
        result = raw.scalar_one_or_none()
        return self._to_dto(result) if raw else None

    async def delete_weather_record(self, record_id: int) -> bool:
        """Deletes a weather record.

        Args:
            record_id: ID of the record.

        Returns:
            bool: True if deleted, False otherwise.
        """
        query = delete(WeatherData).where(WeatherData.id == record_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    @staticmethod
    def _to_dto(instance: WeatherData) -> WeatherResponse:
        return WeatherResponse(
            id=instance.id,
            city=instance.city,
            country=instance.country,
            temperature=instance.temperature,
            humidity=instance.humidity,
            pressure=instance.pressure,
            fetched_at=instance.fetched_at,
        )


