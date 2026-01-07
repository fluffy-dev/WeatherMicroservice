from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class WeatherData(Base):
    """Database model for storing weather information."""

    __tablename__ = "weather_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    country: Mapped[str] = mapped_column(String(10))
    temperature: Mapped[float] = mapped_column(Float)  # Celsius
    humidity: Mapped[int] = mapped_column(Integer)  # Percent
    pressure: Mapped[int] = mapped_column(Integer)  # hPa
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<WeatherData(city={self.city}, temp={self.temperature})>"