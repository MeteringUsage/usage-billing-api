"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.deps import create_connector, ensure_all_schemas
from app.errors import register_exception_handlers
from app.routers import (
    customers,
    events,
    invoices,
    metrics,
    plans,
    subscriptions,
    usage,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    if settings.ensure_schema:
        db = create_connector(settings)
        await db.connect()
        try:
            await ensure_all_schemas(db)
            await db.commit()
        finally:
            await db.disconnect()
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI(
        title="Usage Billing API",
        description=(
            "HTTP API for usage-billing services: metrics, plans, customers, "
            "subscriptions, invoices, usage analytics, and event ingestion."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip()
            for origin in settings.cors_origins.split(",")
            if origin.strip()
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, Any]:
        return {"status": "ok"}

    app.include_router(metrics.router)
    app.include_router(plans.router)
    app.include_router(customers.router)
    app.include_router(subscriptions.router)
    app.include_router(invoices.router)
    app.include_router(usage.router)
    app.include_router(events.router)
    return app


app = create_app()


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
