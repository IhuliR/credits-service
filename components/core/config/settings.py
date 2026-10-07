from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mysql_dsn: str = "mysql+aiomysql://credits:credits@localhost:3306/credits"
    redis_url: str = "redis://localhost:6379/0"
    rabbit_url: str = "amqp://guest:guest@localhost:5672/"

    webhook_secret: str = "change-me"
    generation_cost: int = 10
    balance_cache_ttl_seconds: int = 300
    generations_queue: str = "generations"

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
