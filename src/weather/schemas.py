from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class WeatherBase(BaseModel):
    """Base schema for weather data."""

    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=2, max_length=2)
    temperature: float
    humidity: int = Field(..., ge=0, le=100)
    pressure: int = Field(..., gt=0)


class WeatherCreate(WeatherBase):
    """Schema for creating weather entry."""
    pass


class WeatherUpdate(BaseModel):
    """Schema for updating weather entry (partial update)."""

    temperature: float | None = None
    humidity: int | None = Field(None, ge=0, le=100)
    pressure: int | None = Field(None, gt=0)


class WeatherResponse(WeatherBase):
    """Schema for API responses."""

    id: int
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)