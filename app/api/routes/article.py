from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud
from api.schemes import (
    ReadArticleSchm,
    ReadArticleWithCommentsSchm,
    CreateArticleSchm,
    ChangeArticleSchm,
)
from core import db_helper
from core.utils.redis_utils import redis_cache

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
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    article_in: CreateArticleSchm,
):
    return await crud.create_article(sess, article_in=article_in)


@router.patch("/{article_id}/", response_model=ReadArticleSchm)
async def update_article(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    article_id: int,
    article_in: ChangeArticleSchm,
):
    if not (article_to_update := await crud.get_article(sess, article_id)):
        raise HTTP_404

    return await crud.update_article(sess, article_to_update, article_in)


@router.delete("/{article_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    article_id: int,
):
    if not (article_to_delete := await crud.get_article(sess, article_id)):
        raise HTTP_404

    await crud.delete_article(sess, article_to_delete)
