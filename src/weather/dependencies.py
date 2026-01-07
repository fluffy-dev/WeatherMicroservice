from fastapi import Depends
from typing import Annotated

from src.weather.repository import WeatherRepository

IWeatherRepository: type[WeatherRepository] = Annotated[WeatherRepository, Depends()]
