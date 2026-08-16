"""Usage analytics endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from usage_billing.db import BaseConnector
from usage_billing.usage import UsageService

from app.deps import get_db, get_usage_service
from app.schemas.usage import UsageCheckRequest
from app.serialize import serialize

router = APIRouter(prefix="/usage", tags=["usage"])

DbDep = Annotated[BaseConnector, Depends(get_db)]


def _service(db: BaseConnector) -> UsageService:
    return get_usage_service(db)


@router.get("/analytics")
async def analytics_usage(
    db: DbDep,
    external_customer_id: str = Query(),
    external_subscription_id: str = Query(),
    start_of_period_dt: str = Query(),
    end_of_period_dt: str = Query(),
) -> dict[str, Any]:
    return serialize(
        await _service(db).analytics_usage(
            external_customer_id=external_customer_id,
            external_subscription_id=external_subscription_id,
            start_of_period_dt=start_of_period_dt,
            end_of_period_dt=end_of_period_dt,
        )
    )


@router.get("/current")
async def current_usage(
    db: DbDep,
    external_customer_id: str = Query(),
    external_subscription_id: str = Query(),
    at: datetime | None = Query(default=None),
) -> dict[str, Any]:
    return serialize(
        await _service(db).current_usage(
            external_customer_id=external_customer_id,
            external_subscription_id=external_subscription_id,
            at=at,
        )
    )


@router.post("/check")
async def check_usage_limit(body: UsageCheckRequest, db: DbDep) -> dict[str, Any]:
    return serialize(
        await _service(db).check_limit(
            external_customer_id=body.external_customer_id,
            external_subscription_id=body.external_subscription_id,
            code=body.code,
            units=body.units,
            block_overage=body.block_overage,
        )
    )
