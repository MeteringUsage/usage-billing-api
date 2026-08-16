"""Plan and plan-charge endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from usage_billing.db import BaseConnector
from usage_billing.plan import PlanMetricChargeService, PlanService

from app.deps import get_charge_service, get_db, get_plan_service
from app.errors import require
from app.schemas.common import dump_provided, pagination_params
from app.schemas.plans import (
    PlanChargeCreate,
    PlanChargeUpdate,
    PlanCreate,
    PlanUpdate,
)
from app.serialize import serialize

router = APIRouter(prefix="/plans", tags=["plans"])

DbDep = Annotated[BaseConnector, Depends(get_db)]


def _plans(db: BaseConnector) -> PlanService:
    return get_plan_service(db)


def _charges(db: BaseConnector) -> PlanMetricChargeService:
    return get_charge_service(db)


async def _require_plan(db: BaseConnector, code: str):
    return require(await _plans(db).get(code), f"Unknown plan code: {code}")


@router.post("", status_code=201)
async def create_plan(body: PlanCreate, db: DbDep) -> dict[str, Any]:
    return serialize(await _plans(db).add(**body.model_dump()))


@router.get("")
async def list_plans(
    db: DbDep,
    pagination: Annotated[tuple[int, int], Depends(pagination_params)],
) -> dict[str, Any]:
    page, per_page = pagination
    return serialize(await _plans(db).list(page=page, per_page=per_page))


@router.get("/{code}")
async def get_plan(code: str, db: DbDep) -> dict[str, Any]:
    return serialize(await _require_plan(db, code))


@router.patch("/{code}")
async def update_plan(code: str, body: PlanUpdate, db: DbDep) -> dict[str, Any]:
    payload = dump_provided(body)
    if "code" in payload:
        payload["new_code"] = payload.pop("code")
    return serialize(await _plans(db).update(code, **payload))


@router.delete("/{code}")
async def delete_plan(code: str, db: DbDep) -> dict[str, Any]:
    return serialize(await _plans(db).delete(code))


@router.post("/{code}/charges", status_code=201)
async def create_plan_charge(
    code: str, body: PlanChargeCreate, db: DbDep
) -> dict[str, Any]:
    plan = await _require_plan(db, code)
    return serialize(await _charges(db).add(plan_id=plan.id, **body.model_dump()))


@router.get("/{code}/charges")
async def list_plan_charges(
    code: str,
    db: DbDep,
    pagination: Annotated[tuple[int, int], Depends(pagination_params)],
) -> dict[str, Any]:
    plan = await _require_plan(db, code)
    page, per_page = pagination
    return serialize(
        await _charges(db).list(plan.id, page=page, per_page=per_page)
    )


@router.get("/{code}/charges/{charge_id}")
async def get_plan_charge(code: str, charge_id: int, db: DbDep) -> dict[str, Any]:
    plan = await _require_plan(db, code)
    charge = require(
        await _charges(db).get(plan.id, charge_id),
        f"Unknown plan charge id={charge_id} for plan_id={plan.id}",
    )
    return serialize(charge)


@router.patch("/{code}/charges/{charge_id}")
async def update_plan_charge(
    code: str, charge_id: int, body: PlanChargeUpdate, db: DbDep
) -> dict[str, Any]:
    plan = await _require_plan(db, code)
    return serialize(
        await _charges(db).update(plan.id, charge_id, **dump_provided(body))
    )


@router.delete("/{code}/charges/{charge_id}")
async def delete_plan_charge(
    code: str, charge_id: int, db: DbDep
) -> dict[str, Any]:
    plan = await _require_plan(db, code)
    return serialize(await _charges(db).delete(plan.id, charge_id))
