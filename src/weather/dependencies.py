from fastapi import Depends
from typing import Annotated

from src.weather.repository import WeatherRepository
IWeatherRepository: type[WeatherRepository] = Annotated[WeatherRepository, Depends()]

from src.weather.service import WeatherService
IWeatherService: type[WeatherService] = Annotated[WeatherService, Depends()]
