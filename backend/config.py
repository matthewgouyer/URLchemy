# Code adapted from Real Python Tutorial: https://realpython.com/build-a-python-url-shortener-with-fastapi/
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "sqlite:///data/urls.db"

    class Config:
        env_file = "../.env"

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings