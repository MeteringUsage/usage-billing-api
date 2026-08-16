"""Database connector, schema bootstrap, and service dependencies."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request

from usage_billing.billing import InvoiceService
from usage_billing.customer import CustomerService
from usage_billing.db import BaseConnector, get_connector
from usage_billing.ingestion.core import EventIngestionService
from usage_billing.ingestion.persistence import EventRepository
from usage_billing.metering import BillableMetricService
from usage_billing.plan import PlanMetricChargeService, PlanService
from usage_billing.subscription import SubscriptionService
from usage_billing.usage import UsageService

from app.config import Settings


def create_connector(settings: Settings) -> BaseConnector:
    backend = settings.db_backend
    database_url = settings.database_url

    if database_url:
        if database_url.startswith(("postgres://", "postgresql://")):
            return get_connector("postgres", dsn=database_url)
        if database_url.startswith("sqlite:"):
            path = database_url.removeprefix("sqlite:///")
            return get_connector("sql", database=path)
        if backend in {"postgres", "postgresql"}:
            return get_connector("postgres", dsn=database_url)
        return get_connector("sql", database=database_url)

    if backend in {"postgres", "postgresql"}:
        return get_connector("postgres")
    return get_connector("sql", database=settings.database)


async def ensure_all_schemas(db: BaseConnector) -> None:
    await CustomerService(db).ensure_schema()
    await BillableMetricService(db).ensure_schema()
    await PlanService(db).ensure_schema()
    await PlanMetricChargeService(db).ensure_schema()
    await SubscriptionService(db).ensure_schema()
    await EventRepository(db).ensure_schema()
    await InvoiceService(db).ensure_schema()
    await UsageService(db).ensure_schema()


async def get_db(request: Request) -> AsyncIterator[BaseConnector]:
    settings: Settings = request.app.state.settings
    db = create_connector(settings)
    await db.connect()
    try:
        yield db
        await db.commit()
    except Exception:
        if db.is_connected:
            await db.rollback()
        raise
    finally:
        await db.disconnect()


def get_metric_service(db: BaseConnector) -> BillableMetricService:
    return BillableMetricService(db)


def get_plan_service(db: BaseConnector) -> PlanService:
    return PlanService(db)


def get_charge_service(db: BaseConnector) -> PlanMetricChargeService:
    return PlanMetricChargeService(db)


def get_customer_service(db: BaseConnector) -> CustomerService:
    return CustomerService(db)


def get_subscription_service(db: BaseConnector) -> SubscriptionService:
    return SubscriptionService(db)


def get_invoice_service(db: BaseConnector, request: Request | None = None) -> InvoiceService:
    files_dir = None
    if request is not None:
        settings: Settings = request.app.state.settings
        files_dir = settings.invoice_files
    return InvoiceService(db, files_dir=files_dir)


def get_usage_service(db: BaseConnector) -> UsageService:
    return UsageService(db)


def get_event_repository(db: BaseConnector) -> EventRepository:
    return EventRepository(db)


def get_ingestion_service(db: BaseConnector) -> EventIngestionService:
    return EventIngestionService(EventRepository(db))
