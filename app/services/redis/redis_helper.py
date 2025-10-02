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
        self._client: Redis | None = None

    def redis_client(self) -> Redis:
        if not self._client:
            self._client = Redis(connection_pool=self.pool)
        return self._client

    async def close_pool(self) -> None:
        await self.pool.disconnect()


r_cache = RedisHelper(
    url=str(settings.cache.url),
    encoding=settings.cache.encoding,
    decode_responses=settings.cache.decode_responses,
)
