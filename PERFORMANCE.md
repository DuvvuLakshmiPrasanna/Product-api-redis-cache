# Performance Notes

## Why Caching Improves Performance

For read-heavy access patterns, Redis reduces repeated database round-trips by serving hot product records from memory.

## Implemented Strategy

- Cache-aside on `GET /products/{id}`
- TTL-based expiration via `CACHE_TTL_SECONDS`
- Write-through invalidation on `POST`, `PUT`, and `DELETE`

## Expected Behavior

- First read of a product id: cache miss, DB read, cache set
- Subsequent reads before TTL expiry: cache hit
- After update/delete: cache key invalidated, next read refreshes from DB

## How to Demonstrate

1. Start stack: `docker compose up --build -d`
2. Watch Redis: `docker compose exec redis redis-cli monitor`
3. Call GET for same product id twice
4. Observe first request creates/set key; later request serves hit path

## Validation

Automated tests in `tests/integration/` verify:

- cache miss then hit behavior
- invalidation after update/delete
- graceful fallback when Redis is unavailable
- startup seeding behavior
