"""Billable metric endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from usage_billing.db import BaseConnector
from usage_billing.metering import BillableMetricService

from app.deps import get_db, get_metric_service
from app.errors import require
from app.schemas.common import dump_provided, pagination_params
from app.schemas.metrics import BillableMetricCreate, BillableMetricUpdate
from app.serialize import serialize

router = APIRouter(prefix="/billable-metrics", tags=["billable-metrics"])

DbDep = Annotated[BaseConnector, Depends(get_db)]


def _service(db: BaseConnector) -> BillableMetricService:
    return get_metric_service(db)


@router.post("", status_code=201)
async def create_metric(body: BillableMetricCreate, db: DbDep) -> dict[str, Any]:
    metric = await _service(db).add(**body.model_dump())
    return serialize(metric)


@router.get("")
async def list_metrics(
    db: DbDep,
    pagination: Annotated[tuple[int, int], Depends(pagination_params)],
) -> dict[str, Any]:
    page, per_page = pagination
    return serialize(await _service(db).list(page=page, per_page=per_page))


@router.get("/{code}")
async def get_metric(code: str, db: DbDep) -> dict[str, Any]:
    metric = require(
        await _service(db).get(code),
        f"Unknown billable metric code: {code}",
    )
    return serialize(metric)


@router.patch("/{code}")
async def update_metric(
    code: str, body: BillableMetricUpdate, db: DbDep
) -> dict[str, Any]:
    payload = dump_provided(body)
    if "code" in payload:
        payload["new_code"] = payload.pop("code")
    return serialize(await _service(db).update(code, **payload))


@router.delete("/{code}")
async def delete_metric(code: str, db: DbDep) -> dict[str, Any]:
    return serialize(await _service(db).delete(code))
