import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    auth0_domain: str
    auth0_api_audience: str
    auth0_issuer: str
    auth0_algorithms: str
    auth0_client_id: str
    auth0_client_secret: str
    database_url: str
    env: Literal["development", "production", "test"] = "development"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()