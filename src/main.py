from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.products import router as products_router
from src.config import Settings
from src.database import Base, create_session_factory
from src.services.cache_service import ProductCacheService
from src.services.product_repository import seed_products


def create_app(settings: Settings | None = None, redis_client=None) -> FastAPI:
    app_settings = settings or Settings.from_env()
    engine, session_factory = create_session_factory(app_settings.database_url)
    Base.metadata.create_all(bind=engine)

    with session_factory() as db:
        seed_products(db)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        engine.dispose()

    app = FastAPI(title="Product API with Redis Cache", version="1.0.0", lifespan=lifespan)
    app.state.settings = app_settings
    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.product_cache_service = ProductCacheService(app_settings, redis_client)

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(_request, exc: RequestValidationError):
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    app.include_router(products_router)
    return app


app = create_app()
