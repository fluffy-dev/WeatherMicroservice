from src.exceptions import NotFound


class WeatherNotFound(NotFound):
    """Exception raised when weather data is not found."""
    pass
