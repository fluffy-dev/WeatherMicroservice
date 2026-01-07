from typing import AsyncGenerator, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session.

    Yields:
        AsyncSession: SQLAlchemy async session.
    """
    async with async_session_maker() as session:
        yield session

ISession: type[AsyncSession] = Annotated[AsyncSession, Depends(get_async_session)]