from pathlib import Path

from pydantic import BaseModel, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent


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


class ResponseCache(BaseModel):
    expire: int | None = 7
    inactive: bool = False


class CacheSettings(BaseModel):
    url: RedisDsn
    encoding: str = "utf-8"
    decode_responses: bool = True
    resp: ResponseCache = ResponseCache()


class DataImportSettings(BaseModel):
    article_import_json: Path = BASE_DIR / "import_data" / "articles.json"
    comment_import_json: Path = BASE_DIR / "import_data" / "comments.json"


class ArticlesRouterSettings(BaseModel):
    prefix: str = "/article"
    tag: str = "Articles"


class CommentsRouterSettings(BaseModel):
    prefix: str = "/comment"
    tag: str = "Comments"


class AdministrationRouterSettings(BaseModel):
    prefix: str = "/admin"
    tag: str = "Administration"
    data_import: DataImportSettings = DataImportSettings()


class APIRouterSettings(BaseModel):
    prefix: str = "/api"
    articles: ArticlesRouterSettings = ArticlesRouterSettings()
    comments: CommentsRouterSettings = CommentsRouterSettings()
    admin: AdministrationRouterSettings = AdministrationRouterSettings()


class ArticlesParam(BaseModel):
    title_min_length: int = 4
    title_max_length: int = 120
    text_min_length: int = 2
    topic_min_length: int = 1
    topic_max_length: int = 36
    author_name_max_length: int = 50


class CommentsParam(BaseModel):
    comment_text_min_length: int = 2
    comment_text_max_length: int = 260
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
    comment_param: CommentsParam = CommentsParam()
    db: DBSettings
    cache: CacheSettings


settings = Settings()
