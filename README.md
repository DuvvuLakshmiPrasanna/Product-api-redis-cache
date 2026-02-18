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

**2) Product created via POST /products**

![POST create product](Screenshots/Screenshot%202026-02-18%20161011.png)

**3) Cache miss then set (first GET)**

![Cache miss then set](Screenshots/Screenshot%202026-02-18%20161040.png)

**4) Cache hit (second GET, no SET)**

![Cache hit](Screenshots/Screenshot%202026-02-18%20161948.png)

**5) PUT invalidates cache (DEL)**

![PUT invalidation](Screenshots/Screenshot%202026-02-18%20162113.png)

**6) DELETE invalidates cache and GET returns 404**

![DELETE invalidation + 404](Screenshots/Screenshot%202026-02-18%20162222.png)

**7) Redis down fallback (GET still returns 200)**

![Redis fallback](Screenshots/Screenshot%202026-02-18%20162322.png)

## Demo Video

- Demo link (2-5 minutes): <add your video link here>

## Quick Demo Flow (for video)

1. Create product via `POST /products`.
2. First `GET /products/{id}` (cache miss, DB read + cache set).
3. Second `GET /products/{id}` (cache hit).
4. Update with `PUT /products/{id}` (cache invalidated).
5. Delete with `DELETE /products/{id}` and show `GET` returns `404`.

## Demo Script (2-5 minutes)

1. `docker compose up --build`
2. `curl.exe http://localhost:8080/health`
3. Start monitor: `docker compose exec redis redis-cli monitor`
4. Create product (POST) and copy `id`
5. First GET (miss): show `GET` then `SET` in monitor
6. Second GET (hit): show only `GET`
7. PUT update: show `DEL` in monitor
8. DELETE: show `DEL` in monitor, then GET returns `404`
9. `docker compose stop redis`
10. GET existing product: returns `200` (fallback)
11. `docker compose start redis`

## TTL Demo (Optional but recommended)

1. Set `CACHE_TTL_SECONDS=5` in `.env.example` or environment.
2. Restart stack: `docker compose up --build -d`
3. Start monitor: `docker compose exec redis redis-cli monitor`
4. GET product (expect `GET` + `SET`)
5. Wait 6 seconds.
6. GET product again (expect `GET` + `SET` again due to TTL expiry)

## Submission Instructions

Publish a **public GitHub repository** with the following mandatory artifacts:

- Application code: complete backend source under `src/`
- Comprehensive `README.md` (this file), including:
  - Project title and description
  - Setup/build/run instructions
  - Automated test instructions
  - API documentation with request/response examples
  - Caching strategy explanation (cache-aside + invalidation)
  - Design decisions summary
  - Screenshots section
  - Demo video link
- `docker-compose.yml`
- `.env.example`
- `Dockerfile`
- `tests/` with automated test suite

Optional bonus artifacts:

- `ARCHITECTURE.md` (included)
- `PERFORMANCE.md` (included)

## Evaluation Overview

The project is designed to be evaluated on:

- Functional correctness of API endpoints and status codes
- Cache behavior: miss, hit, and invalidation after write operations
- Resilience when Redis is unavailable (fallback to DB path)
- Code quality and maintainability
- Documentation clarity and completeness

This repository includes integration tests covering endpoint behavior, cache flow, invalidation, validation, and startup seeding.

## Common Mistakes to Avoid

- Missing cache invalidation after `POST`, `PUT`, or `DELETE`
- No fallback path when Redis read/write fails
- Hardcoded config instead of environment variables
- Weak test coverage for cache hit/miss/invalidation
- Incomplete API docs and setup/test instructions
- Missing input validation on product payloads

## FAQ

**Q: Can I use PostgreSQL/MySQL instead of SQLite?**  
A: Yes. The caching behavior is the core requirement; persistence technology is flexible.

**Q: Is authentication required?**  
A: No. Auth is out of scope for this assignment.

**Q: Do I need `GET /products` list endpoint?**  
A: Not required. The core requirement is `GET /products/{id}` with cache-aside behavior.

**Q: How do I demonstrate cache hit/miss in a demo?**  
A: Use Redis monitor (`redis-cli monitor`) while calling `GET /products/{id}` twice for the same id.

**Q: Can I use an ORM?**  
A: Yes. This implementation uses SQLAlchemy.

**Q: How do I run tests inside the API container?**  
A: `docker compose exec api-service python -m pytest tests/`
