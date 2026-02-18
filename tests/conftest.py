import fakeredis
import pytest
from fastapi.testclient import TestClient

from src.config import Settings
from src.main import create_app
from src.models.product import Product


@pytest.fixture
def test_client(tmp_path):
    db_file = tmp_path / "test.db"
    settings = Settings(
        api_port=8080,
        redis_host="localhost",
        redis_port=6379,
        cache_ttl_seconds=120,
        database_url=f"sqlite:///{db_file}",
    )
    fake_redis = fakeredis.FakeRedis(decode_responses=True)
    app = create_app(settings=settings, redis_client=fake_redis)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_client_with_broken_redis(tmp_path):
    class BrokenRedis:
        def get(self, *_args, **_kwargs):
            raise RuntimeError("redis down")

        def set(self, *_args, **_kwargs):
            raise RuntimeError("redis down")

        def delete(self, *_args, **_kwargs):
            raise RuntimeError("redis down")

    db_file = tmp_path / "test_broken.db"
    settings = Settings(
        api_port=8080,
        redis_host="localhost",
        redis_port=6379,
        cache_ttl_seconds=120,
        database_url=f"sqlite:///{db_file}",
    )
    app = create_app(settings=settings, redis_client=BrokenRedis())
    with TestClient(app) as client:
        yield client


@pytest.fixture
def seeded_product_id(test_client):
    payload = {
        "name": "Test Product",
        "description": "Product for integration tests",
        "price": 9.99,
        "stock_quantity": 12,
    }
    response = test_client.post("/products", json=payload)
    assert response.status_code == 201
    return response.json()["id"]
