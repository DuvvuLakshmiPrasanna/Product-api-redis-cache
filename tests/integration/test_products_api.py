from src.models.product import Product


def test_create_product_returns_201(test_client):
    payload = {
        "name": "Created Product",
        "description": "Created through API",
        "price": 29.99,
        "stock_quantity": 42,
    }

    response = test_client.post("/products", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["name"] == payload["name"]


def test_get_product_cache_miss_then_hit(test_client, seeded_product_id):
    first_response = test_client.get(f"/products/{seeded_product_id}")
    assert first_response.status_code == 200

    session_factory = test_client.app.state.session_factory
    with session_factory() as db:
        product = db.get(Product, seeded_product_id)
        db.delete(product)
        db.commit()

    second_response = test_client.get(f"/products/{seeded_product_id}")
    assert second_response.status_code == 200
    assert second_response.json()["id"] == seeded_product_id


def test_put_invalidates_cache_and_returns_updated_product(test_client, seeded_product_id):
    first_get = test_client.get(f"/products/{seeded_product_id}")
    assert first_get.status_code == 200

    update_payload = {"price": 19.99, "stock_quantity": 7}
    update_response = test_client.put(f"/products/{seeded_product_id}", json=update_payload)

    assert update_response.status_code == 200
    assert update_response.json()["price"] == 19.99
    assert update_response.json()["stock_quantity"] == 7

    read_after_update = test_client.get(f"/products/{seeded_product_id}")
    assert read_after_update.status_code == 200
    assert read_after_update.json()["price"] == 19.99


def test_delete_invalidates_cache_and_get_returns_404(test_client, seeded_product_id):
    assert test_client.get(f"/products/{seeded_product_id}").status_code == 200

    delete_response = test_client.delete(f"/products/{seeded_product_id}")
    assert delete_response.status_code == 204

    get_after_delete = test_client.get(f"/products/{seeded_product_id}")
    assert get_after_delete.status_code == 404


def test_input_validation_for_post_and_put(test_client):
    bad_post = test_client.post(
        "/products",
        json={"name": "", "description": "x", "price": -1, "stock_quantity": -2},
    )
    assert bad_post.status_code == 400

    create_resp = test_client.post(
        "/products",
        json={
            "name": "Valid",
            "description": "Valid",
            "price": 10.0,
            "stock_quantity": 1,
        },
    )
    product_id = create_resp.json()["id"]

    bad_put = test_client.put(f"/products/{product_id}", json={})
    assert bad_put.status_code == 400


def test_redis_failure_gracefully_falls_back_to_db(test_client_with_broken_redis):
    create_response = test_client_with_broken_redis.post(
        "/products",
        json={
            "name": "No Redis",
            "description": "Redis unavailable",
            "price": 11.0,
            "stock_quantity": 3,
        },
    )
    assert create_response.status_code == 201

    product_id = create_response.json()["id"]
    get_response = test_client_with_broken_redis.get(f"/products/{product_id}")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == product_id
