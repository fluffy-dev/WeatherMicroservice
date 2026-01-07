from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WeatherEntity:
    city: str
    country: str
    temperature: float
    humidity: int
    pressure: int

