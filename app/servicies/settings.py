import secrets

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_prefix: str = "/api"

    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str

    postgres_user: str
    postgres_password: str

    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_file=".env")

    def build_postgres_dsn(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
