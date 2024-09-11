from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud
from api.schemes import (
    ReadArticleSchm,
    ReadArticleWithCommentsSchm,
    CreateArticleSchm,
)
from core import db_helper

router = APIRouter()


@router.get("/{article_id}/", response_model=ReadArticleWithCommentsSchm)
async def get_article(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    article_id: int,
):
    if result := await crud.get_article_with_five_last_comments(sess, article_id):
        return result

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="article not found",
    )


@router.get("/", response_model=Sequence[ReadArticleSchm])
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
