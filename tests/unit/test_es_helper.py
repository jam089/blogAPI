import pytest
from core.config import settings
from elastic_transport import ConnectionError
from pytest_mock import MockFixture
from services.elasticsearch.es_helper import ESHelper


@pytest.mark.asyncio
async def test_es_connect_success(mocker: MockFixture) -> None:
    mocker.patch.object(settings.es, "connection_ping", 1)
    fake_client = mocker.Mock()
    fake_client.ping = mocker.AsyncMock(side_effect=[False, True])
    mocker.patch(
        "services.elasticsearch.es_helper.AsyncElasticsearch",
        return_value=fake_client,
    )

    es = ESHelper(url_list=["http://localhost:9200"])
    conn = await es.es_connect()

    assert conn is fake_client
    assert es._connection is fake_client
    fake_client.ping.assert_awaited()


@pytest.mark.asyncio
async def test_es_close_connection(mocker: MockFixture) -> None:
    fake_client = mocker.AsyncMock()

    es = ESHelper(url_list=["http://localhost:9200"])
    es._connection = fake_client

    await es.es_close_connection()

    fake_client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_es_close_connection_without_connection() -> None:
    es = ESHelper(url_list=["http://localhost:9200"])
    await es.es_close_connection()


def test_get_es_connection_success(mocker: MockFixture) -> None:
    fake_client = mocker.AsyncMock()
    es = ESHelper(url_list=["http://localhost:9200"])
    es._connection = fake_client

    conn = es.get_es_connection()

    assert conn is fake_client


def test_get_es_connection_raises() -> None:
    es = ESHelper(url_list=["http://localhost:9200"])
    with pytest.raises(ConnectionError):
        es.get_es_connection()
