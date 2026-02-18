# High-Performance Product API with Redis Cache-Aside Pattern

A production-style backend API built with FastAPI, SQLite, and Redis implementing **cache-aside caching**, **TTL**, and **cache invalidation on writes**.

## Features

- RESTful product endpoints:
  - `POST /products`
  - `GET /products/{id}`
  - `PUT /products/{id}`
  - `DELETE /products/{id}`
- Cache-aside read path for `GET /products/{id}`
- Cache invalidation on `POST`, `PUT`, and `DELETE`
- Configurable cache TTL via environment variable
- Graceful fallback to database when Redis is unavailable
- Input validation for POST/PUT payloads
- Automatic database seeding on startup (3 sample products)
- Dockerized app + Redis via single `docker compose up` command
- Automated tests for API behavior and cache scenarios

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy + SQLite
- Redis (`redis-py`)
- Pytest + Fakeredis
- Docker + Docker Compose

## Project Structure

```text
product-api-redis-cache/
├── src/
│   ├── api/
│   │   └── products.py
│   ├── models/
│   │   └── product.py
│   ├── schemas/
│   │   └── product.py
│   ├── services/
│   │   ├── cache_service.py
│   │   └── product_repository.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   └── main.py
├── tests/
│   └── integration/
│       ├── test_products_api.py
│       └── test_startup_seeding.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Environment Variables

Defined in `.env.example`:

- `API_PORT`: API listening port
- `REDIS_HOST`: Redis hostname
- `REDIS_PORT`: Redis port
- `CACHE_TTL_SECONDS`: default Redis TTL for product cache entries
- `DATABASE_URL`: database connection string

## Run with Docker

```bash
git clone <repo>
cd product-api-redis-cache
docker compose up --build
```

If you already cloned the repo, the last two commands are sufficient.

```bash
docker compose up --build
```

API base URL: `http://localhost:8080`

Health check:

```bash
curl http://localhost:8080/health
```

## Run Tests

### Local

```bash
pip install -r requirements.txt
pytest -q
```

### Inside API Container (required command format)

```bash
docker compose exec api-service pytest -q tests/
```

Exact command requested by the assignment (also valid):

```bash
docker compose exec api-service python -m pytest tests/
```

## Testing Environment Setup

- Start stack: `docker compose up --build -d`
- Run tests in running API container: `docker compose exec api-service pytest -q tests/`
- Optional one-shot test run: `docker compose run --rm api-service pytest -q tests/`

This verifies API behavior in the same Docker Compose network where the `api-service` can reach `redis` by hostname.

## Database Seeding

On startup, the app seeds sample products automatically only when the products table is empty.

- Seed logic: `src/services/product_repository.py -> seed_products`
- Startup trigger: `src/main.py -> create_app` (calls `seed_products` after table creation)
- Seed count: 3 sample products by default
- Non-duplication: seeding is skipped when data already exists

## API Documentation

FastAPI Swagger UI:

- `http://localhost:8080/docs`

### 1) Create Product

**POST** `/products`

Request:

```json
{
  "name": "Example Product",
  "description": "A detailed description of the product.",
  "price": 29.99,
  "stock_quantity": 100
}
```

Response: `201 Created`

```json
{
  "id": "<generated-uuid>",
  "name": "Example Product",
  "description": "A detailed description of the product.",
  "price": 29.99,
  "stock_quantity": 100
}
```

### 2) Get Product by ID

**GET** `/products/{id}`

- `200 OK` with product if found
- `404 Not Found` if not found

### 3) Update Product by ID

**PUT** `/products/{id}`

Request (partial or full):

```json
{
  "price": 34.99,
  "stock_quantity": 95
}
```

- `200 OK` with updated product
- `400 Bad Request` if request body has no fields
- `404 Not Found` if product does not exist

### 4) Delete Product by ID

**DELETE** `/products/{id}`

- `204 No Content` if deleted
- `404 Not Found` if product not found

### 5) Health Check

**GET** `/health`

Response: `200 OK`

```json
{ "status": "ok" }
```

## Input Validation Edge Cases

### Invalid POST (missing required fields)

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8080/products -ContentType "application/json" -Body '{"price":100}'
```

Expected: `400 Bad Request` with validation errors.

### Invalid PUT (negative values)

```powershell
Invoke-RestMethod -Method Put -Uri http://localhost:8080/products/<id> -ContentType "application/json" -Body '{"stock_quantity":-5}'
```

Expected: `400 Bad Request` with validation errors.

## Caching Strategy Implemented

### Cache-Aside (Read)

For `GET /products/{id}`:

1. Check Redis key `product:{id}`.
2. If present, return cached value (**cache hit**).
3. If missing, read from DB (**cache miss**), store in Redis with `CACHE_TTL_SECONDS`, then return.

### Invalidation (Write)

For successful `POST`, `PUT`, and `DELETE`:

1. Write to primary DB first.
2. Invalidate Redis key `product:{id}`.

This ensures stale data is not served after write operations.

### TTL Purpose

- Prevents stale data from lingering in cache indefinitely.
- Controls memory usage under heavy read traffic.
- Configured via `CACHE_TTL_SECONDS`.

### Redis Failure Handling

If Redis operations fail (get/set/delete), the API logs a warning and continues serving data from the DB path where possible.

## Design Decisions

- **FastAPI** for high performance and automatic OpenAPI docs.
- **SQLAlchemy + SQLite** for simple reliable persistence suitable for assignment scope.
- **Service separation** for repository logic and cache logic for maintainability.
- **Config via environment variables** for production-style deployment flexibility.
- **Docker multi-stage build** to keep image optimized.

## Architecture Summary

- **API layer:** FastAPI handles routing, validation, and response schema.
- **Service layer:** `cache_service` encapsulates Redis access and error handling.
- **Repository layer:** `product_repository` encapsulates DB access and seeding.
- **Persistence:** SQLite via SQLAlchemy for simple, reliable storage.
- **Cache keys:** `product:{id}` for clean lookup and invalidation.

## Suggested Submission Artifacts

Add these before final submission:

- Postman/Insomnia screenshots for each endpoint
- Redis monitor screenshot showing miss then hit (`redis-cli monitor`)
- 2-5 minute demo video link

## Screenshots

Screenshots captured during live verification of health, cache-aside behavior, invalidation, TTL expiry, and Redis fallback.

**1) API health check**

![API health check](Screenshots/Screenshot%202026-02-18%20160838.png)

This confirms the service is running and responding with `{"status":"ok"}` on `/health`.

**2) Product created via POST /products**

![POST create product](Screenshots/Screenshot%202026-02-18%20161011.png)

Shows a successful create request returning `201 Created` with a generated `id` and the full product payload.

**3) Cache miss then set (first GET)**

![Cache miss then set](Screenshots/Screenshot%202026-02-18%20161040.png)

First read hits the DB and then writes to Redis with `SET` and TTL, proving cache-aside miss behavior.

**4) Cache hit (second GET, no SET)**

![Cache hit](Screenshots/Screenshot%202026-02-18%20161948.png)

Second read shows only `GET` in Redis with no `SET`, confirming the response was served from cache.

**5) PUT invalidates cache (DEL)**

![PUT invalidation](Screenshots/Screenshot%202026-02-18%20162113.png)

Update triggers a `DEL` for `product:{id}`, ensuring stale cache entries are removed.

**6) DELETE invalidates cache and GET returns 404**

![DELETE invalidation + 404](Screenshots/Screenshot%202026-02-18%20162222.png)

Deletion removes the cache entry and a follow-up `GET` returns `404 Not Found`.

**7) Redis down fallback (GET still returns 200)**

![Redis fallback](Screenshots/Screenshot%202026-02-18%20162322.png)

Demonstrates that when Redis is unavailable the API falls back to the DB and still returns data successfully.

## Additional Notes

- Cache keys use the format `product:{id}` for predictable invalidation.
- Redis errors are logged and do not crash the API.
- Startup seeding inserts sample products only when the database is empty.
