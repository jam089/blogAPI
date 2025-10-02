import asyncio
import logging

from core import settings
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError

logger = logging.getLogger("uvicorn.elastic_search")


class ESHelper:
    def __init__(
        self,
        url_list: list[str],
    ):
        self.url_list = url_list
        self.request_timeout = settings.es.request_timeout_s
        self._connection: AsyncElasticsearch | None = None

    async def es_connect(self) -> AsyncElasticsearch:
        self._connection = AsyncElasticsearch(
            hosts=self.url_list,
            request_timeout=self.request_timeout,
        )
        ping = False
        logger.info("Connectin to ES...")
        while not ping:
            ping = await self._connection.ping()
            logger.info("Still try to connect ot ES...")
            await asyncio.sleep(7)
        logger.info("ES connection established")
        return self._connection

    async def es_close_connection(self) -> None:
        if self._connection:
            await self._connection.close()

    def get_es_connection(self) -> AsyncElasticsearch:
        if self._connection:
            return self._connection
        else:
            raise ConnectionError("ES connection not established yet.")


es = ESHelper(
    url_list=[str(settings.es.url)],
)
