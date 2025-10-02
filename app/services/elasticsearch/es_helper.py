import asyncio
import logging

from core import settings
from elasticsearch import AsyncElasticsearch


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
        connection = AsyncElasticsearch(
            hosts=self.url_list,
            request_timeout=self.request_timeout,
        )
        self._connection = connection
        ping = False
        logger.info("Connectin to ES...")
        while not ping:
            ping = await connection.ping()
            logger.info("Still try to connect ot ES...")
            await asyncio.sleep(7)
        logger.info("ES connection established")
        return connection

    def es_close_connection(self) -> None:
        self._connection.close()

    def get_es_connection(self) -> AsyncElasticsearch:
        return self._connection


es = ESHelper(
    url_list=[str(settings.es.url)],
)
