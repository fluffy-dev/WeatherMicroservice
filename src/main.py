from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import settings
from src.weather.router import router as weather_router
from src.utils import logger, setup_logging
from src.exceptions import NotFound


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events: startup and shutdown logic."""
    setup_logging()
    logger.info("Starting Weather Service...")
    yield
    logger.info("Shutting down Weather Service...")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


@app.exception_handler(NotFound)
async def not_found_exception_handler(request: Request, exc: NotFound):
    """Global exception handler for NotFound exceptions."""
    logger.error(f"Resource not found: {exc}")
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


app.include_router(weather_router)


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}