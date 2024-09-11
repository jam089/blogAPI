from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from .comment import ReadCommentSchm

from core import settings


class BaseArticleSchm(BaseModel):
    pass


class CreateArticleSchm(BaseArticleSchm):
    title: str = Field(
        min_length=settings.article_param.title_min_length,
        max_length=settings.article_param.title_max_length,
    )
    text: str = Field(min_length=settings.article_param.text_min_length)
    topic: str = Field(
        min_length=settings.article_param.topic_min_length,
        max_length=settings.article_param.topic_max_length,
    )
    author_name: str = Field(max_length=settings.article_param.author_name_max_length)


class ChangeArticleSchm(BaseArticleSchm):
    title: str | None = Field(
        None,
        min_length=settings.article_param.title_min_length,
        max_length=settings.article_param.title_max_length,
    )
    text: str | None = Field(
        None,
        min_length=settings.article_param.text_min_length,
    )
    topic: str | None = Field(
        None,
        min_length=settings.article_param.topic_min_length,
        max_length=settings.article_param.topic_max_length,
    )
    author_name: str | None = Field(
        None, max_length=settings.article_param.author_name_max_length
    )


class ReadArticleSchm(CreateArticleSchm):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    last_updated_at: datetime | None = None
    score: float


class ReadArticleWithCommentsSchm(ReadArticleSchm):
    comments: List[ReadCommentSchm] | None = None
