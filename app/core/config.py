from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class DBSettings(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class ArticlesRouterSettings(BaseModel):
    prefix: str = "/article"
    tag: str = "Articles"


class CommentsRouterSettings(BaseModel):
    prefix: str = "/comment"
    tag: str = "Comments"


class APIRouterSettings(BaseModel):
    prefix: str = "/api"
    articles: ArticlesRouterSettings = ArticlesRouterSettings()
    comments: CommentsRouterSettings = CommentsRouterSettings()


class ArticlesParam(BaseModel):
    title_min_length: int = 4
    title_max_length: int = 120
    text_min_length: int = 2
    topic_min_length: int = 1
    topic_max_length: int = 36
    author_name_max_length: int = 50


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env.template", ".env"],
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="blogAPI__",
    )

    run: RunSettings = RunSettings()
    api: APIRouterSettings = APIRouterSettings()
    article_param: ArticlesParam = ArticlesParam()
    db: DBSettings


settings = Settings()
