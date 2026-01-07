from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_TITLE: str = "Weather Async Microservice"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis & Celery
    REDIS_HOST: str
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # External API (OpenWeatherMap)
    WEATHER_API_KEY: str
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Logic
    CITIES_TO_TRACK: list[str] = ["London", "Almaty", "New York", "Tokyo", "Moscow"]
    UPDATE_INTERVAL_SECONDS: int = 3600

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()