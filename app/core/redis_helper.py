from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from redis import Redis

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

    @asynccontextmanager
    async def rclient_getter(self) -> AsyncGenerator[Redis, None]:
        pool = redis.ConnectionPool.from_url(
            url=self.url,
            encoding=self.encoding,
            decode_responses=self.decode_responses,
        )
        client = redis.Redis(connection_pool=pool)
        yield client
        await client.close()


r_cache = RedisHelper(
    url=str(settings.cache.url),
    encoding=settings.cache.encoding,
    decode_responses=settings.cache.decode_responses,
)
