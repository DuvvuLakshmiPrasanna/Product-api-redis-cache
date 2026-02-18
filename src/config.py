import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_port: int = 8080
    redis_host: str = "redis"
    redis_port: int = 6379
    cache_ttl_seconds: int = 3600
    database_url: str = "sqlite:///./products.db"

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            api_port=int(os.getenv("API_PORT", "8080")),
            redis_host=os.getenv("REDIS_HOST", "redis"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./products.db"),
        )
