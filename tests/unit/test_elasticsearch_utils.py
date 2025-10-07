import pytest
from elasticsearch.exceptions import BadRequestError
from pydantic import BaseModel
from pytest_mock import MockFixture
from services.elasticsearch.elasticsearch_utils import (
    check_index,
    create_index,
    get_doc,
    indexing_docs,
    remove_doc,
    searching_docs,
)


class UserSchema(BaseModel):
    id: str
    name: str


@pytest.mark.asyncio
async def test_create_index_success(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    expected_response = {"acknowledged": True}
    es_session.indices.create.return_value = expected_response

    index_name = "test_index"
    index_map = {"field1": {"type": "text"}}

    result = await create_index(es_session, index_name, index_map)

    assert result == expected_response

    es_session.indices.create.assert_awaited_once_with(
        index=index_name,
        body={"mappings": {"properties": {**index_map}}},
        ignore=400,
    )


@pytest.mark.asyncio
async def test_create_index_called_with_correct_body(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    es_session.indices.create.return_value = {"acknowledged": True}

    index_name = "another_index"
    index_map = {"title": {"type": "keyword"}}

    await create_index(es_session, index_name, index_map)

    called_args, called_kwargs = es_session.indices.create.call_args

    assert called_kwargs["index"] == index_name
    assert called_kwargs["ignore"] == 400
    assert "mappings" in called_kwargs["body"]
    assert called_kwargs["body"]["mappings"]["properties"] == index_map


@pytest.mark.asyncio
async def test_check_index_exists(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    es_session.indices.exists.return_value = True
    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.es.get_es_connection",
        return_value=es_session,
    )

    result = await check_index("existing_index")

    assert result is None
    es_session.indices.exists.assert_awaited_once_with(index="existing_index")


@pytest.mark.asyncio
async def test_check_index_not_exists_creates_index(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    es_session.indices.exists.return_value = False
    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.es.get_es_connection",
        return_value=es_session,
    )

    mocker.patch.dict(
        "services.elasticsearch.elasticsearch_utils.index_dict",
        {"new_index": {"field": {"type": "text"}}},
    )

    expected_response = mocker.MagicMock()
    expected_response.body = {}
    es_create_mock = mocker.patch(
        "services.elasticsearch.elasticsearch_utils.create_index",
        return_value=expected_response,
    )

    result = await check_index("new_index")

    assert result == expected_response
    es_session.indices.exists.assert_awaited_once_with(index="new_index")
    es_create_mock.assert_awaited_once_with(
        es_session=es_session,
        index_name="new_index",
        index_map={"field": {"type": "text"}},
    )


@pytest.mark.asyncio
async def test_check_index_not_exists_no_index_map(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    es_session.indices.exists.return_value = False
    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.es.get_es_connection",
        return_value=es_session,
    )

    mocker.patch.dict("services.elasticsearch.elasticsearch_utils.index_dict", {})

    result = await check_index("missing_index")

    assert result is None
    es_session.indices.exists.assert_awaited_once_with(index="missing_index")


@pytest.mark.asyncio
async def test_check_index_create_index_error(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    es_session.indices.exists.return_value = False
    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.es.get_es_connection",
        return_value=es_session,
    )

    mocker.patch.dict(
        "services.elasticsearch.elasticsearch_utils.index_dict",
        {"bad_index": {"field": {"type": "text"}}},
    )

    bad_response = mocker.MagicMock()
    bad_response.body = {"error": "something went wrong"}
    bad_response.meta = {"status": 400}
    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.create_index",
        return_value=bad_response,
    )

    with pytest.raises(BadRequestError):
        await check_index("bad_index")


@pytest.mark.asyncio
async def test_indexing_docs_empty_index(mocker: MockFixture) -> None:
    db_session = mocker.Mock()
    es_session = mocker.AsyncMock()
    es_session.cat.indices.return_value = [{"docs.count": "0"}]

    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.get_data_to_indexing",
        return_value=[{"_id": 1, "_source": {"field": "value"}}],
    )

    async_bulk_mock = mocker.patch(
        "services.elasticsearch.elasticsearch_utils.async_bulk",
        return_value=(1, []),
    )

    result = await indexing_docs(
        db_session,
        es_session,
        "test_index",
        sql_model=mocker.Mock(),
        pydantic_schm=mocker.Mock(),
    )

    assert result == {"success": 1, "failed": []}
    es_session.delete_by_query.assert_not_awaited()
    async_bulk_mock.assert_awaited_once()


@pytest.mark.asyncio
async def indexing_docs_with_docs(mocker: MockFixture) -> None:
    db_session = mocker.Mock()
    es_session = mocker.AsyncMock()
    es_session.cat.indices.return_value = [{"docs.count": "5"}]

    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.get_data_to_indexing",
        return_value=[{"_id": 1, "_source": {"field": "value"}}],
    )

    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.async_bulk",
        return_value=(2, [10]),
    )

    result = await indexing_docs(
        db_session,
        es_session,
        "test_index",
        sql_model=mocker.Mock(),
        pydantic_schm=mocker.Mock(),
    )

    assert result == {"success": 2, "failed": [10]}
    es_session.delete_by_query.assert_awaited_once_with(
        index="test_index", query={"match_all": {}}
    )


@pytest.mark.asyncio
async def test_remove_doc_not_exists(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()

    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.check_doc", return_value=False
    )

    result = await remove_doc(es_session, "test_index", 42)

    assert result is None
    es_session.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_remove_doc_exists(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    es_session.delete.return_value = {"result": "deleted"}

    mocker.patch(
        "services.elasticsearch.elasticsearch_utils.check_doc", return_value=True
    )

    result = await remove_doc(es_session, "test_index", 42)

    assert result == {"result": "deleted"}
    es_session.delete.assert_awaited_once_with(
        index="test_index",
        id="42",
    )


@pytest.mark.asyncio
async def test_searching_docs_returns_ids(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    fake_response = mocker.Mock()
    fake_response.body = {
        "hits": {
            "hits": [
                {"_id": "1", "_source": {"name": "doc1"}},
                {"_id": "2", "_source": {"name": "doc2"}},
            ]
        }
    }
    es_session.search.return_value = fake_response

    response, ids = await searching_docs(es_session, "test_index", "query text")

    es_session.search.assert_awaited_once()
    args, kwargs = es_session.search.call_args
    assert kwargs["index"] == "test_index"
    assert "multi_match" in kwargs["body"]["query"]

    assert ids == [1, 2]
    assert response is fake_response


@pytest.mark.asyncio
async def test_searching_docs_ignores_docs_without_id(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    fake_response = mocker.Mock()
    fake_response.body = {
        "hits": {
            "hits": [
                {"_id": "10", "_source": {"name": "ok"}},
                {"_source": {"name": "missing_id"}},
            ]
        }
    }
    es_session.search.return_value = fake_response

    _, ids = await searching_docs(es_session, "test_index", "something")

    assert ids == [10]


@pytest.mark.asyncio
async def test_get_doc_without_pydantic(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    es_session.get.return_value = mocker.Mock(
        body={"_id": "42", "_source": {"field": "value"}}
    )

    result = await get_doc(es_session, "test_index", 42)

    assert result == {"_id": "42", "_source": {"field": "value"}}
    es_session.get.assert_awaited_once_with(index="test_index", id="42")


@pytest.mark.asyncio
async def test_get_doc_with_pydantic(mocker: MockFixture) -> None:
    es_session = mocker.AsyncMock()
    es_session.get.return_value = mocker.Mock(
        body={"_id": "123", "_source": {"name": "Alice"}}
    )

    result = await get_doc(es_session, "users", 123, pydantic_schm=UserSchema)

    assert isinstance(result, UserSchema)
    assert result.id == "123"
    assert result.name == "Alice"
    es_session.get.assert_awaited_once_with(index="users", id="123")
