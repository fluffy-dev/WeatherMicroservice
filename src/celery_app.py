from celery import Celery
from src.config import settings

celery_app = Celery(
    "weather_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.weather.tasks"]
)

celery_app.conf.beat_schedule = {
    "fetch-weather-every-hour": {
        "task": "src.weather.tasks.update_weather_data",
        "schedule": settings.UPDATE_INTERVAL_SECONDS,
    },
}
celery_app.conf.timezone = "UTC"