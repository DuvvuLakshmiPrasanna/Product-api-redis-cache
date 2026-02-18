# Architecture Overview

## Components

- `api-service` (FastAPI): Handles REST endpoints and cache-aside workflow
- `redis` (Redis): Stores cached product payloads by key `product:{id}`
- `sqlite` (via SQLAlchemy): Primary persistent store for products

## Request Flow

### GET /products/{id}

1. API checks Redis key `product:{id}`.
2. On hit: returns cached JSON immediately.
3. On miss: reads from DB, writes to Redis with TTL, returns response.

### POST/PUT/DELETE /products

1. API writes to DB first.
2. API invalidates Redis key `product:{id}`.
3. Next GET for that id performs fresh DB read and recaches.

## Resilience

- Redis failures are logged and do not crash request handling.
- API falls back to DB path when cache operations fail.

## Configuration

All runtime settings come from environment variables:

- `API_PORT`
- `REDIS_HOST`
- `REDIS_PORT`
- `CACHE_TTL_SECONDS`
- `DATABASE_URL`

## Deployment

Docker Compose orchestrates:

- `api-service`
- `redis`

Health checks are configured for both services.
