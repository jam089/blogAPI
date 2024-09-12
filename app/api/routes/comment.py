from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud
from api.schemes import ReadCommentSchm
from core import db_helper

router = APIRouter()

HTTP_404 = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="comment not found",
)


@router.get("/{comment_id}", response_model=ReadCommentSchm)
async def get_comment(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    comment_id: int,
):
    if comment := await crud.get_comment(sess, comment_id):
        return comment

    raise HTTP_404
