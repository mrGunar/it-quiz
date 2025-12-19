from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings
from app.main import app
from app.database import Base, get_db

if not settings.TEST_DATABASE_URL:
    raise Exception("Please provide an URL for the test database in the `.env` file.")

engine = create_async_engine(settings.TEST_DATABASE_URL, echo=False, future=True)


TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function", autouse=True)
async def setup_test_database():
    """Create and drop tables for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Get a fresh database session."""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def async_client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with overridden dependency."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
