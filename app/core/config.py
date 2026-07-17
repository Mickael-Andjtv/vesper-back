from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Vesper"
    HF_TOKEN: Optional[str] = None
    HF_MODEL: Optional[str] = None
    GROQ_MODEL: str | None = None
    API_URL: str = ""
    GROQ_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
