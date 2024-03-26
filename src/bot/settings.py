from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_file=".env")

    bot_token: SecretStr
    bot_name: str
    use_webhook: bool = False

    postgres_host: str
    postgres_db: str
    postgres_password: str
    postgres_port: int = 5432
    postgres_user: str
    redis_host: str
    redis_port: int = 6379

    secret: str
    # redis_host: str
    # redis_port: int
    # redis_database: int

    def build_postgres_dsn(self) -> str:
        return (
            "postgresql://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    def redis_dsn(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"
