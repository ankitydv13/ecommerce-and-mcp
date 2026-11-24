from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "ecommerce"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "Cfg@1234567"

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    jwt_issuer: str = "ecommerce-api"
    jwt_audience: str = "ecommerce-api"
    admin_user_ids: set[int] = Field(default_factory=set)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


setting = Setting()