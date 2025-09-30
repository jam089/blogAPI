from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator

from redis.asyncio import Redis, ConnectionPool

from core import settings


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

    async def redis_getter(self) -> AsyncGenerator[Redis, None]:
        async with self.redis_client() as redis_sess:
            yield redis_sess
            await redis_sess.close()


r_cache = RedisHelper(
    url=str(settings.cache.url),
    encoding=settings.cache.encoding,
    decode_responses=settings.cache.decode_responses,
)
