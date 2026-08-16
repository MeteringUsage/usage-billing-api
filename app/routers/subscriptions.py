"""Subscription endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from usage_billing.db import BaseConnector
from usage_billing.subscription import SubscriptionService, SubscriptionStatus

from app.deps import get_db, get_subscription_service
from app.errors import require
from app.schemas.common import dump_provided, pagination_params
from app.schemas.subscriptions import (
    SubscriptionCreate,
    SubscriptionTerminate,
    SubscriptionUpdate,
)
from app.serialize import serialize

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

DbDep = Annotated[BaseConnector, Depends(get_db)]


def _service(db: BaseConnector) -> SubscriptionService:
    return get_subscription_service(db)


@router.post("", status_code=201)
async def create_subscription(
    body: SubscriptionCreate, db: DbDep
) -> dict[str, Any]:
    return serialize(await _service(db).add(**body.model_dump()))


@router.get("")
async def list_subscriptions(
    db: DbDep,
    pagination: Annotated[tuple[int, int], Depends(pagination_params)],
    external_customer_id: str | None = Query(default=None),
    status: SubscriptionStatus | None = Query(default=None),
) -> dict[str, Any]:
    page, per_page = pagination
    return serialize(
        await _service(db).list(
            external_customer_id=external_customer_id,
            status=status,
            page=page,
            per_page=per_page,
        )
    )


@router.get("/{external_id}")
async def get_subscription(external_id: str, db: DbDep) -> dict[str, Any]:
    subscription = require(
        await _service(db).get(external_id),
        f"Unknown subscription external_id: {external_id}",
    )
    return serialize(subscription)


@router.patch("/{external_id}")
async def update_subscription(
    external_id: str, body: SubscriptionUpdate, db: DbDep
) -> dict[str, Any]:
    return serialize(await _service(db).update(external_id, **dump_provided(body)))


@router.post("/{external_id}/terminate")
async def terminate_subscription(
    external_id: str, db: DbDep, body: SubscriptionTerminate | None = None
) -> dict[str, Any]:
    payload = dump_provided(body) if body is not None else {}
    return serialize(await _service(db).terminate(external_id, **payload))
