from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RunSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class Settings(BaseSettings):
    run: RunSettings = RunSettings()


settings = Settings()
