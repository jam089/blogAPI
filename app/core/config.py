from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env.template", ".env"],
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="blogAPI__",
    )

    run: RunSettings = RunSettings()


settings = Settings()
