from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseCommentSchm(BaseModel):
    pass


class CreateCommentSchm(BaseCommentSchm):
    comment_text: str = Field(max_length=260)
    author_name: str = Field(max_length=50)
    score: int = Field(ge=1, le=10)
    article_id: int


class ChangeCommentSchm(BaseCommentSchm):
    comment_text: str | None = Field(None, max_length=260)
    author_name: str | None = Field(None, max_length=50)
    score: int | None = Field(None, ge=1, le=10)


class ReadCommentSchm(CreateCommentSchm):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    last_updated_at: datetime | None = None
