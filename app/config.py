from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    yandex_api_key: str
    gateway_url: str
    zoom_threshold: int = 18

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()