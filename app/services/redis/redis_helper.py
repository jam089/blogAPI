from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator

from core import settings
from redis.asyncio import ConnectionPool, Redis


class RedisHelper:
    def __init__(
        self,
        url: str,
        encoding: str,
        decode_responses: bool,
    ):
        self.url = url
        self.encoding = encoding
        self.decode_responses = decode_responses
        self.pool = ConnectionPool.from_url(
            url=self.url,
            encoding=self.encoding,
            decode_responses=self.decode_responses,
        )

    @asynccontextmanager
    async def redis_client(self) -> AsyncIterator[Redis]:
        redis_client = Redis(connection_pool=self.pool)
        yield redis_client
        await redis_client.close()


r_cache = RedisHelper(
    url=str(settings.cache.url),
    encoding=settings.cache.encoding,
    decode_responses=settings.cache.decode_responses,
)
