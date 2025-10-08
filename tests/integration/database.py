from collections.abc import AsyncGenerator

import pytest
from core import db_helper, settings
from core.models import Base
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

test_engine = create_async_engine(
    url=str(settings.db.url),
    poolclass=NullPool,
)
test_session_factory = async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def override_dispose() -> None:
    await test_engine.dispose()


async def override_session_getter() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


app.dependency_overrides[db_helper.session_getter] = override_session_getter
app.dependency_overrides[db_helper.dispose] = override_dispose


@pytest.fixture(autouse=True)
async def prepare_db() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with test_session_factory() as conn:
        await conn.begin()
        await conn.execute(
            text(
                """
            CREATE OR REPLACE FUNCTION update_last_update_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.last_update_at = NOW();
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
            CREATE TRIGGER last_update_trigger
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_last_update_column();
            """
            )
        )
        await conn.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url=f"http://test{settings.api.prefix}",
        follow_redirects=False,
        headers={"Cache-Control": "no-cache"},
    ) as ac:
        yield ac
