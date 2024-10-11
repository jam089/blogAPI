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
)
from core import db_helper, settings
from core.models import Article
from services.redis import redis_cache
from services.elasticsearch import es, add_doc, update_doc

router = APIRouter()

HTTP_404 = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="article not found",
)


@router.get("/trends/", response_model=Sequence[ReadArticleSchm])
@redis_cache(model_type=Sequence[ReadArticleSchm])
async def get_trends_articles(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    return await crud.get_trend_articles(sess)


@router.get("/{article_id}/", response_model=ReadArticleWithCommentsSchm)
async def get_article(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    article_id: int,
):
    if result := await crud.get_article(sess, article_id):
        return result

    raise HTTP_404


@router.get("/", response_model=Sequence[ReadArticleSchm])
@redis_cache(model_type=Sequence[ReadArticleSchm])
async def get_all_articles(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
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
):
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
):
    if not (article_to_update := await crud.get_article(db_sess, article_id)):
        raise HTTP_404

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
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    article_id: int,
):
    if not (article_to_delete := await crud.get_article(sess, article_id)):
        raise HTTP_404

    await crud.delete_article(sess, article_to_delete)
