from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud
from api.schemes import ReadCommentSchm, CreateCommentSchm, ChangeCommentSchm
from core import db_helper

router = APIRouter()

HTTP_404_comment = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="comment not found",
)

HTTP_404_article = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="article not found",
)


@router.get("/article/{article_id}/", response_model=Sequence[ReadCommentSchm])
async def get_comments_of_article(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    article_id: int,
):
    if article := await crud.get_article(sess, article_id):
        return await crud.get_comments_of_article(sess, article)

    raise HTTP_404_article


@router.get("/{comment_id}/", response_model=ReadCommentSchm)
async def get_comment(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    comment_id: int,
):
    if comment := await crud.get_comment(sess, comment_id):
        return comment

    raise HTTP_404_comment


@router.post(
    "/",
    response_model=ReadCommentSchm,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    comment_in: CreateCommentSchm,
):
    if await crud.get_article(sess, comment_in.article_id):
        return await crud.create_comment(sess, comment_in)

    raise HTTP_404_article


@router.patch("/{comment_id}/", response_model=ReadCommentSchm)
async def update_comment(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    comment_id: int,
    comment_in: ChangeCommentSchm,
):
    if comment_to_update := await crud.get_comment(sess, comment_id):
        return await crud.update_comment(sess, comment_to_update, comment_in)

    raise HTTP_404_comment


@router.delete("/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    comment_id: int,
):
    if not (comment_to_delete := await crud.get_comment(sess, comment_id)):
        raise HTTP_404_comment

    await crud.delete_comment(sess, comment_to_delete)
