"""FastAPI application entry point.

Bootstrap order:
    1. load settings  (app.core.config)
    2. construct FastAPI app with metadata
    3. install middleware stack
        CORS → TraceID → RateLimit → JWT → Audit (response side)
    4. register routers under /api/v1/*
    5. wire exception handlers so every error becomes a uniform APIResponse
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.cache import create_cache
from app.core.config import get_settings
from app.core.exceptions import install_exception_handlers
from app.db.session import init_engine
from app.middleware.audit import AuditMiddleware
from app.middleware.auth import JWTAuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.trace import TraceIDMiddleware
from app.routers import (
    audit,
    auth,
    benchmark,
    demos,
    encoding,
    keys,
    pubkey,
    scenarios,
    symmetric,
)
from app.routers import (
    hash as hash_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Wire long-lived resources (DB pool, Redis client) at boot."""
    init_engine()
    yield
    cache = getattr(app.state, "cache", None)
    if cache is not None:
        await cache.close()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="CryptoLab API",
        description=(
            "Hand-written cryptographic primitives behind a JWT-authenticated "
            "REST API. See /docs for the OpenAPI explorer."
        ),
        version="0.1.0",
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )
    app.state.cache = create_cache()

    # CORS — explicit whitelist; never use "*" in prod.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Trace-Id"],
    )

    # Order matters: outermost → innermost on request path.
    app.add_middleware(AuditMiddleware)
    app.add_middleware(JWTAuthMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TraceIDMiddleware)

    install_exception_handlers(app)

    # ----- routers -----
    api_prefix = "/api/v1"
    app.include_router(auth.router,        prefix=f"{api_prefix}/auth",      tags=["auth"])
    app.include_router(symmetric.router,   prefix=f"{api_prefix}/symmetric", tags=["symmetric"])
    app.include_router(hash_router.router, prefix=f"{api_prefix}/hash",      tags=["hash"])
    app.include_router(encoding.router,    prefix=f"{api_prefix}/encoding",  tags=["encoding"])
    app.include_router(pubkey.router,      prefix=f"{api_prefix}/pubkey",    tags=["pubkey"])
    app.include_router(scenarios.router,   prefix=f"{api_prefix}/scenarios", tags=["scenarios"])
    app.include_router(keys.router,        prefix=f"{api_prefix}/keys",      tags=["keys"])
    app.include_router(audit.router,       prefix=f"{api_prefix}/audit",     tags=["audit"])
    app.include_router(demos.router,       prefix=f"{api_prefix}/demos",     tags=["demos"])
    app.include_router(benchmark.router,   prefix=f"{api_prefix}/benchmark", tags=["benchmark"])

    @app.get("/healthz", include_in_schema=False)
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
