from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from src.database import get_db_session
from src.services.cache_service import ProductCacheService


def get_db(request: Request) -> Generator[Session, None, None]:
    yield from get_db_session(request.app.state.session_factory)


def get_product_cache_service(request: Request) -> ProductCacheService:
    return request.app.state.product_cache_service
