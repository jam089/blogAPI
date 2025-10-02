from typing import Any, AsyncGenerator, List, Sequence, Type, TypeVar, cast

from core.models import Base
from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncScalarResult

from services.elasticsearch.es_helper import es
from services.elasticsearch.es_index_mapping import index_dict

T = TypeVar("T", bound=Base)


async def create_index(
    es_session: AsyncElasticsearch,
    index_name: str,
    index_map: dict,
) -> ObjectApiResponse[dict[str, Any]]:
    index_body = {"mappings": {"properties": {**index_map}}}
    response = await es_session.indices.create(  # type: ignore[call-arg]
        index=index_name,
        body=index_body,
        ignore=400,
    )
    return response


async def check_index(
    index_name: str,
) -> ObjectApiResponse[dict[str, Any]] | None:
    es_session: AsyncElasticsearch = es.get_es_connection()
    if not await es_session.indices.exists(index=index_name):
        index_map: dict | None = index_dict.get(index_name)
        if index_map is None:
            return None
        response = await create_index(
            es_session=es_session,
            index_name=index_name,
            index_map=index_map,
        )
        return response
    return None


async def get_data_to_indexing(
    db_session: AsyncSession,
    index_name: str,
    sql_model: Type[T],
    pydantic_schm: Type[BaseModel],
) -> AsyncGenerator[dict, None]:
    stmt = select(sql_model)
    stream: AsyncScalarResult = await db_session.stream_scalars(stmt)

    async for sql_obj in stream:  # type: T
        data_for_es = pydantic_schm.model_validate(sql_obj)
        yield {
            "_index": index_name,
            "_id": sql_obj.id,
            "_source": data_for_es.model_dump(),
        }


async def indexing_docs(
    db_session: AsyncSession,
    es_session: AsyncElasticsearch,
    index_name: str,
    sql_model: Type[Base],
    pydantic_schm: Type[BaseModel],
) -> dict[str, int | List[int]]:
    index_info = cast(
        list[dict[str, str]],
        await es_session.cat.indices(
            index=index_name,
            format="json",
        ),
    )

    if (docs_qty := index_info[0].get("docs.count")) and int(docs_qty):
        query: dict[str, dict] = {"match_all": {}}
        await es_session.delete_by_query(index=index_name, query=query)

    success, failed = await async_bulk(
        client=es_session,
        actions=get_data_to_indexing(
            db_session,
            index_name,
            sql_model,
            pydantic_schm,
        ),
    )
    response = {
        "success": success,
        "failed": failed,
    }
    return response


async def add_doc(
    es_session: AsyncElasticsearch,
    index_name: str,
    sql_object: Base,
    pydantic_schm: Type[BaseModel],
) -> ObjectApiResponse[dict]:
    data_for_es = pydantic_schm.model_validate(sql_object)
    response = await es_session.index(
        index=index_name,
        id=str(sql_object.id),
        document=data_for_es.model_dump(),
    )
    return response


async def update_doc(
    es_session: AsyncElasticsearch,
    index_name: str,
    doc_id: int,
    pydantic_object: BaseModel,
) -> ObjectApiResponse[dict]:
    response = await es_session.update(
        index=index_name,
        id=str(doc_id),
        doc=pydantic_object.model_dump(exclude_unset=True),
    )
    return response


async def remove_doc(
    es_session: AsyncElasticsearch,
    index_name: str,
    doc_id: int,
) -> ObjectApiResponse[dict] | None:

    if not await check_doc(es_session, index_name, doc_id):
        return None

    response = await es_session.delete(
        index=index_name,
        id=str(doc_id),
    )
    return response


async def searching_docs(
    es_session: AsyncElasticsearch,
    index_name: str,
    searching_string: str,
) -> tuple[ObjectApiResponse, List[int]]:
    index_mapping: dict = index_dict[index_name]
    searching_query = {
        "query": {
            "multi_match": {
                "query": searching_string,
                "fields": [*index_mapping.keys()],
            }
        },
        "_source": {"excludes": ["text"]},
    }

    response: ObjectApiResponse = await es_session.search(
        index=index_name,
        body=searching_query,
    )

    hits = response.body["hits"]["hits"]
    matched_ids = [int(doc.get("_id")) for doc in hits if "_id" in doc]

    return response, matched_ids


async def check_doc(
    es_session: AsyncElasticsearch,
    index_name: str,
    doc_id: int,
) -> bool:
    doc_exist = await es_session.exists_source(
        index=index_name,
        id=str(doc_id),
    )
    return doc_exist.body


async def get_doc(
    es_session: AsyncElasticsearch,
    index_name: str,
    doc_id: int,
    pydantic_schm: Type[BaseModel] | None = None,
) -> BaseModel | dict[str, Any]:
    doc: ObjectApiResponse[dict[str, Any]] = await es_session.get(
        index=index_name, id=str(doc_id)
    )

    if pydantic_schm:
        doc_dict = {
            "id": doc.body.get("_id"),
            **doc.body["_source"],
        }
        return pydantic_schm(**doc_dict)

    return doc.body
