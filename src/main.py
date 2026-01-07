from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.weather.router import router as weather_router
from src.utils import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events: startup and shutdown logic."""
    logger.info("Starting Weather Service...")
    yield
    logger.info("Shutting down Weather Service...")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(weather_router)


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}