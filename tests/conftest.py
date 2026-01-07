import asyncio
from typing import AsyncGenerator

import pytest
import asyncpg
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.database import Base, get_async_session
from src.main import app
from src.config import settings

TEST_DB_NAME = f"{settings.POSTGRES_DB}_test"

TEST_DATABASE_URL = settings.DATABASE_URL.replace(settings.POSTGRES_DB, TEST_DB_NAME)

engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
async_session_maker_test = async_sessionmaker(engine_test, expire_on_commit=False)


# Helper functions
async def create_database():
    sys_conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database="postgres"
    )

    try:
        await sys_conn.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
            AND pid <> pg_backend_pid();
        """)
        await sys_conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
        await sys_conn.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    finally:
        await sys_conn.close()


async def drop_database():
    sys_conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database="postgres"
    )
    try:
        await sys_conn.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{TEST_DB_NAME}'
            AND pid <> pg_backend_pid();
        """)
        await sys_conn.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
    finally:
        await sys_conn.close()


#Fixtures

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def manage_database(event_loop):
    await create_database()

    Base.metadata.bind = engine_test

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine_test.dispose()
    await drop_database()


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker_test() as session:
        yield session
        await session.execute(text("TRUNCATE TABLE weather_data RESTART IDENTITY CASCADE;"))
        await session.commit()


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    async with async_session_maker_test() as session:
        await session.execute(text("TRUNCATE TABLE weather_data RESTART IDENTITY CASCADE;"))
        await session.commit()