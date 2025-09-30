from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator

from core import settings

from elasticsearch import AsyncElasticsearch


class ESHelper:
    def __init__(
        self,
        url_list: list[str],
    ):
        self.url_list = url_list

    @asynccontextmanager
    async def es_client(self) -> AsyncIterator[AsyncElasticsearch]:
        es_client = AsyncElasticsearch(hosts=self.url_list)
        yield es_client
        await es_client.close()

    async def es_getter(self) -> AsyncGenerator[AsyncElasticsearch, None]:
        async with self.es_client() as es_sess:
            yield es_sess
            await es_sess.close()


es = ESHelper(
    url_list=[str(settings.es.url)],
)
