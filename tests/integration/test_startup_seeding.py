import fakeredis
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from src.config import Settings
from src.main import create_app
from src.models.product import Product


def _product_count(app) -> int:
    session_factory = app.state.session_factory
    with session_factory() as db:
        return db.execute(select(func.count(Product.id))).scalar_one()


def test_startup_seeds_products_when_database_is_empty(tmp_path):
    db_file = tmp_path / "seeded.db"
    settings = Settings(
        api_port=8080,
        redis_host="localhost",
        redis_port=6379,
        cache_ttl_seconds=120,
        database_url=f"sqlite:///{db_file}",
    )

    app = create_app(settings=settings, redis_client=fakeredis.FakeRedis(decode_responses=True))
    with TestClient(app):
        seeded_count = _product_count(app)

    assert 3 <= seeded_count <= 5


def test_startup_does_not_duplicate_seed_data(tmp_path):
    db_file = tmp_path / "seeded_once.db"
    settings = Settings(
        api_port=8080,
        redis_host="localhost",
        redis_port=6379,
        cache_ttl_seconds=120,
        database_url=f"sqlite:///{db_file}",
    )

    first_app = create_app(settings=settings, redis_client=fakeredis.FakeRedis(decode_responses=True))
    with TestClient(first_app):
        first_count = _product_count(first_app)

    second_app = create_app(settings=settings, redis_client=fakeredis.FakeRedis(decode_responses=True))
    with TestClient(second_app):
        second_count = _product_count(second_app)

    assert first_count == second_count
