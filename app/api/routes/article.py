from typing import Annotated, Sequence

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud
from api.schemes import (
    ReadArticleSchm,
    ReadArticleWithCommentsSchm,
    CreateArticleSchm,
    ChangeArticleSchm,
    ArticleSearchResponseSchm,
    ESReadArticleSchm,
)
from core import db_helper, settings
from core.models import Article
from services.redis import redis_cache
from services.elasticsearch import (
    es,
    add_doc,
    update_doc,
    remove_doc,
    searching_docs,
    check_doc,
    get_doc,
)

router = APIRouter()

HTTP_404 = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="article not found",
)


@router.get("/trends/", response_model=Sequence[ReadArticleSchm])
@redis_cache(model_type=Sequence[ReadArticleSchm])
async def get_trends_articles(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Sequence[Article]:
    return await crud.get_trend_articles(sess)


@router.get("/search/", response_model=ArticleSearchResponseSchm)
async def search_articles(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    es_sess: Annotated[AsyncElasticsearch, Depends(es.es_getter)],
    query: str,
) -> dict[str, Article | dict]:
    search_response, article_ids_list = await searching_docs(
        es_session=es_sess,
        index_name=settings.es.articles_index,
        searching_string=query,
    )

    articles = {}

    for article_id in article_ids_list:
        article: Article | None = await crud.get_article(db_sess, article_id)
        if not article:
            break
        articles.update(
            {article_id: ReadArticleSchm.model_validate(article).model_dump()}
        )

    return {
        "articles": articles,
        "search_response": search_response.body,
    }


@router.get("/{article_id}/", response_model=ReadArticleWithCommentsSchm)
async def get_article(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    article_id: int,
) -> Article:
    if result := await crud.get_article(sess, article_id):
        return result

    raise HTTP_404


@router.get("/", response_model=Sequence[ReadArticleSchm])
@redis_cache(model_type=Sequence[ReadArticleSchm])
async def get_all_articles(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> Sequence[Article]:
    return await crud.get_all_articles(sess)


@router.post(
    "/",
    response_model=ReadArticleSchm,
    status_code=status.HTTP_201_CREATED,
)
async def create_article(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    es_sess: Annotated[AsyncElasticsearch, Depends(es.es_getter)],
    article_in: CreateArticleSchm,
) -> Article:
    article: Article = await crud.create_article(db_sess, article_in=article_in)
    await add_doc(
        es_session=es_sess,
        index_name=settings.es.articles_index,
        sql_object=article,
        pydantic_schm=CreateArticleSchm,
    )
    return article


@router.patch("/{article_id}/", response_model=ReadArticleSchm)
async def update_article(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    es_sess: Annotated[AsyncElasticsearch, Depends(es.es_getter)],
    article_id: int,
    article_in: ChangeArticleSchm,
) -> Article:
    if not (article_to_update := await crud.get_article(db_sess, article_id)):
        raise HTTP_404

    if not await check_doc(
        es_session=es_sess,
        index_name=settings.es.articles_index,
        doc_id=article_id,
    ):
        await add_doc(
            es_session=es_sess,
            index_name=settings.es.articles_index,
            sql_object=article_to_update,
            pydantic_schm=CreateArticleSchm,
        )

    article_before_update_in_pydantic = ESReadArticleSchm.model_validate(
        article_to_update
    )
    es_article_before_update_in_pydantic = await get_doc(
        es_session=es_sess,
        index_name=settings.es.articles_index,
        doc_id=article_id,
        pydantic_schm=ESReadArticleSchm,
    )

    if not (article_before_update_in_pydantic == es_article_before_update_in_pydantic):
        await add_doc(
            es_session=es_sess,
            index_name=settings.es.articles_index,
            sql_object=article_to_update,
            pydantic_schm=CreateArticleSchm,
        )

    article: Article = await crud.update_article(db_sess, article_to_update, article_in)

    await update_doc(
        es_session=es_sess,
        index_name=settings.es.articles_index,
        doc_id=article_id,
        pydantic_object=article_in,
    )

    return article


@router.delete("/{article_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    es_sess: Annotated[AsyncElasticsearch, Depends(es.es_getter)],
    article_id: int,
) -> None:
    if not (article_to_delete := await crud.get_article(db_sess, article_id)):
        raise HTTP_404

    await crud.delete_article(db_sess, article_to_delete)

    await remove_doc(
        es_session=es_sess,
        index_name=settings.es.articles_index,
        doc_id=article_id,
    )
