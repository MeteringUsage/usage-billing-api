"""Customer endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from usage_billing.customer import CustomerService
from usage_billing.db import BaseConnector

from app.deps import get_customer_service, get_db
from app.errors import require
from app.schemas.common import dump_provided, pagination_params
from app.schemas.customers import CustomerCreate, CustomerUpdate
from app.serialize import serialize

router = APIRouter(prefix="/customers", tags=["customers"])

DbDep = Annotated[BaseConnector, Depends(get_db)]


def _service(db: BaseConnector) -> CustomerService:
    return get_customer_service(db)


@router.post("", status_code=201)
async def create_customer(body: CustomerCreate, db: DbDep) -> dict[str, Any]:
    return serialize(await _service(db).add(**body.model_dump()))


@router.get("")
async def list_customers(
    db: DbDep,
    pagination: Annotated[tuple[int, int], Depends(pagination_params)],
) -> dict[str, Any]:
    page, per_page = pagination
    return serialize(await _service(db).list(page=page, per_page=per_page))


@router.get("/{external_id}")
async def get_customer(external_id: str, db: DbDep) -> dict[str, Any]:
    customer = require(
        await _service(db).get(external_id),
        f"Unknown customer external_id: {external_id}",
    )
    return serialize(customer)


@router.patch("/{external_id}")
async def update_customer(
    external_id: str, body: CustomerUpdate, db: DbDep
) -> dict[str, Any]:
    return serialize(await _service(db).update(external_id, **dump_provided(body)))


@router.delete("/{external_id}")
async def delete_customer(external_id: str, db: DbDep) -> dict[str, Any]:
    return serialize(await _service(db).delete(external_id))
