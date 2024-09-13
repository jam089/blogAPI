from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud
from core import db_helper, settings
from core.utils.file_utils import json_read

router = APIRouter()


@router.get("/import-data/", status_code=status.HTTP_201_CREATED)
async def import_data_from_file(
    sess: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    articles_flg = await crud.bulk_load_article(
        sess,
        json_read(settings.api.admin.data_import.article_import_json),
    )
    comments_flg = await crud.bulk_load_comments(
        sess,
        json_read(settings.api.admin.data_import.comment_import_json),
    )
    await crud.inactive_imported_articles(sess)

    if not (articles_flg and comments_flg):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="can not process import data",
        )
