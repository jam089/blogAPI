from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseArticleSchm(BaseModel):
    pass


class CreateArticleSchm(BaseArticleSchm):
    title: str = Field(max_length=120)
    text: str = Field(min_length=260)
    topic: str = Field(max_length=36)
    author_name: str = Field(max_length=50)


class ChangeArticleSchm(BaseArticleSchm):
    title: str | None = Field(None, max_length=120)
    text: str | None = Field(None, min_length=260)
    topic: str | None = Field(None, max_length=36)
    author_name: str | None = Field(None, max_length=50)


class ReadArticleSchm(CreateArticleSchm):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    last_updated_at: datetime | None = None
    result_score: float | 0 = 0
