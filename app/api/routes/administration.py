from typing import Annotated, List

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api import crud
from core import db_helper, settings
from core.utils.file_utils import json_read
from core.models import Article
from api.schemes import CreateArticleSchm
from services.elasticsearch import index_docs, es

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


@router.get("/es_index_articles/")
async def index_articles(
    db_sess: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    es_sess: Annotated[AsyncElasticsearch, Depends(es.es_getter)],
) -> dict[str, int | List[int]]:
    return await index_docs(
        db_session=db_sess,
        es_session=es_sess,
        index_name=settings.es.articles_index,
        sql_model=Article,
        pydantic_schm=CreateArticleSchm,
    )
