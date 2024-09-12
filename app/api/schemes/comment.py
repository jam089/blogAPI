from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core import settings


class BaseCommentSchm(BaseModel):
    pass


class CreateCommentSchm(BaseCommentSchm):
    comment_text: str = Field(
        min_length=settings.comment_param.comment_text_min_length,
        max_length=settings.comment_param.comment_text_max_length,
    )
    author_name: str = Field(max_length=settings.comment_param.author_name_max_length)
    score: int = Field(ge=1, le=10)
    article_id: int


class ChangeCommentSchm(BaseCommentSchm):
    comment_text: str | None = Field(
        None,
        min_length=settings.comment_param.comment_text_min_length,
        max_length=settings.comment_param.comment_text_max_length,
    )
    author_name: str | None = Field(
        None,
        max_length=settings.comment_param.author_name_max_length,
    )
    score: int | None = Field(None, ge=1, le=10)


class ReadCommentSchm(CreateCommentSchm):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    last_updated_at: datetime | None = None
