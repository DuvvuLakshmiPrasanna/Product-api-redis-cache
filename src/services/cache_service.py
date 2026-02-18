import json
import logging

import redis

from src.config import Settings
from src.schemas.product import ProductResponse

logger = logging.getLogger(__name__)


class ProductCacheService:
    def __init__(self, settings: Settings, redis_client: redis.Redis | None = None):
        self.settings = settings
        self._client = redis_client or redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True,
            socket_timeout=1,
            socket_connect_timeout=1,
        )

    @staticmethod
    def _cache_key(product_id: str) -> str:
        return f"product:{product_id}"

    def get_product_from_cache(self, product_id: str) -> ProductResponse | None:
        try:
            cached_json = self._client.get(self._cache_key(product_id))
            if not cached_json:
                return None
            data = json.loads(cached_json)
            return ProductResponse(**data)
        except Exception as exc:
            logger.warning("Redis get failed; falling back to DB. reason=%s", exc)
            return None

    def set_product_in_cache(self, product: ProductResponse) -> None:
        try:
            self._client.set(
                self._cache_key(product.id),
                product.model_dump_json(),
                ex=self.settings.cache_ttl_seconds,
            )
        except Exception as exc:
            logger.warning("Redis set failed; continuing without cache. reason=%s", exc)

    def invalidate_product_cache(self, product_id: str) -> None:
        try:
            self._client.delete(self._cache_key(product_id))
        except Exception as exc:
            logger.warning("Redis delete failed; continuing. reason=%s", exc)
