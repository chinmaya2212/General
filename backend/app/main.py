from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import validation_exception_handler, global_exception_handler
from app.core.middleware import ContentSizeLimitMiddleware, AuthPrepMiddleware, SecureHeadersMiddleware
from app.api.v1.router import api_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

def create_app() -> FastAPI:
    # 1. Setup structured logging
    setup_logging()
    
    logger.info("Starting Application Bootstrap...")
    
    # Secure Config Validation at Startup
    try:
        settings.validate_critical_settings()
        logger.info("Configuration validation passed.")
    except ValueError as e:
        logger.error(str(e))
        import sys
        sys.exit(1)
    
    # 2. Initialize FastAPI app with OpenAPI metadata
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="FastAPI Backend for AI Security Intelligence Platform MVP",
        version="1.0.0",
        lifespan=lifespan
    )

    # 3. Setup Middlewares
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    app.add_middleware(ContentSizeLimitMiddleware)
    app.add_middleware(SecureHeadersMiddleware)
    app.add_middleware(AuthPrepMiddleware)

    # 4. Global Exception Handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # 5. Include API Routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # 6. Top-level health for deployment orchestrators
    @app.get("/health", tags=["Health"])
    def root_health():
        return {"status": "ok"}
        
    logger.info("Bootstrap complete.")

    return app

app = create_app()
