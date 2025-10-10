import os
from typing import AsyncGenerator

import pytest_asyncio
from core import settings
from elasticsearch import AsyncElasticsearch
from redis.asyncio.client import ConnectionPool, Redis


@pytest_asyncio.fixture
async def es_client(
    elasticsearch_service: str,
) -> AsyncGenerator[AsyncElasticsearch, None]:
    client = AsyncElasticsearch(hosts=[elasticsearch_service])
    yield client
    await client.close()


@pytest_asyncio.fixture
async def redis_client(redis_service: dict) -> AsyncGenerator[Redis, None]:
    url = f"redis://:{os.environ.get("BLOGAPI__CACHE__PASS")}@{redis_service["host"]}:{str(redis_service["port"])}/0"
    pool = ConnectionPool.from_url(
        url=url,
        encoding=settings.cache.encoding,
        decode_responses=settings.cache.decode_responses,
    )
    yield Redis(connection_pool=pool)
    await pool.disconnect()
