import os
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from core import db_helper, settings
from core.models import Base
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


@pytest.fixture(scope="package", autouse=True)
def test_db_url(pg_service: dict[str, Any]) -> str:
    user = os.environ["BLOGAPI__DB__LOGIN"]
    password = os.environ["BLOGAPI__DB__PASS"]
    db_name = os.environ["BLOGAPI__DB__SCHEMA"]
    return f"postgresql+asyncpg://{user}:{password}@{pg_service['host']}:{pg_service['port']}/{db_name}"


@pytest.fixture(scope="package")
def create_test_engine(test_db_url: str) -> AsyncEngine:
    test_engine = create_async_engine(
        url=test_db_url,
        poolclass=NullPool,
    )
    return test_engine


@pytest.fixture(scope="package")
def create_test_session_factory(
    create_test_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    test_session_factory = async_sessionmaker(
        bind=create_test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return test_session_factory


@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_dependency(
    create_test_engine: AsyncEngine,
    create_test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[None, None]:
    async def override_dispose() -> None:
        await create_test_engine.dispose()

    async def override_session_getter() -> AsyncGenerator[AsyncSession, None]:
        async with create_test_session_factory() as session:
            yield session

    app.dependency_overrides[db_helper.session_getter] = override_session_getter
    app.dependency_overrides[db_helper.dispose] = override_dispose

    yield


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_db(
    create_test_engine: AsyncEngine,
    create_test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[None, None]:
    async with create_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with create_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with create_test_session_factory() as conn:
        await conn.begin()
        await conn.execute(
            text(
                """
                CREATE OR REPLACE FUNCTION update_last_updated_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_updated_at = NOW();
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                """
            )
        )
        await conn.commit()
        await conn.execute(
            text(
                """
                CREATE TRIGGER last_updated_trigger
                BEFORE UPDATE ON articles
                FOR EACH ROW
                EXECUTE FUNCTION update_last_updated_column();
                """
            )
        )
        await conn.commit()
        await conn.execute(
            text(
                """
                CREATE TRIGGER last_updated_trigger
                BEFORE UPDATE ON comments
                FOR EACH ROW
                EXECUTE FUNCTION update_last_updated_column();
                """
            )
        )
        await conn.commit()

    yield

    async with create_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_session(
    create_test_session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with create_test_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(app_service: str) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url=f"http://test{settings.api.prefix}",
        follow_redirects=False,
        headers={"Cache-Control": "no-cache"},
    ) as ac:
        yield ac
