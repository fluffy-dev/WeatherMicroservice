from sqlalchemy import select, delete, update
from src.weather.models import WeatherData
from src.weather.schemas import WeatherUpdate, WeatherResponse
from src.weather.entity import WeatherEntity
from src.weather.exceptions import WeatherNotFound

from src.database import ISession


class WeatherRepository:
    """Service layer for weather business logic."""

    def __init__(self, session: ISession):
        self.session = session

    async def create_weather_record(self, data: WeatherEntity) -> WeatherResponse:
        """
        Creates a new weather record in the database.

        Args:
            data (WeatherEntity): The weather data entity to persist.

        Returns:
            WeatherResponse: The created weather record as a DTO.
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

    async def get_latest_weather(self, city: str) -> WeatherResponse:
        """
        Retrieves the latest weather record for a specific city.

        Args:
            city (str): The name of the city.

        Returns:
            WeatherResponse: The latest weather record.

        Raises:
            WeatherNotFound: If no weather data exists for the specified city.
        """
        query = (
            select(WeatherData)
            .where(WeatherData.city == city)
            .order_by(WeatherData.fetched_at.desc())
            .limit(1)
        )
        raw = await self.session.execute(query)
        result = raw.scalar_one_or_none()
        
        if not result:
            raise WeatherNotFound(f"Weather data for city '{city}' not found.")
            
        return self._to_dto(result)

    async def update_weather_record(
            self,
            record_id: int,
            data: WeatherUpdate
    ) -> WeatherResponse:
        """
        Updates an existing weather record.

        Args:
            record_id (int): The ID of the record to update.
            data (WeatherUpdate): The data to update.

        Returns:
            WeatherResponse: The updated weather record.

        Raises:
            WeatherNotFound: If the weather record with the given ID does not exist.
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
        
        if not result:
            raise WeatherNotFound(f"Weather record with ID {record_id} not found.")

        return self._to_dto(result)

    async def delete_weather_record(self, record_id: int) -> None:
        """
        Deletes a weather record from the database.

        Args:
            record_id (int): The ID of the record to delete.

        Raises:
            WeatherNotFound: If the weather record with the given ID does not exist.
        """
        query = delete(WeatherData).where(WeatherData.id == record_id)
        result = await self.session.execute(query)
        await self.session.commit()
        
        if result.rowcount == 0:
            raise WeatherNotFound(f"Weather record with ID {record_id} not found.")

    @staticmethod
    def _to_dto(instance: WeatherData) -> WeatherResponse:
        """Converts a database model instance to a Data Transfer Object."""
        return WeatherResponse(
            id=instance.id,
            city=instance.city,
            country=instance.country,
            temperature=instance.temperature,
            humidity=instance.humidity,
            pressure=instance.pressure,
            fetched_at=instance.fetched_at,
        )


