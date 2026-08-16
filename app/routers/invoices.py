"""Invoice endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response

from usage_billing.billing import InvoiceService, InvoiceStatus, PaymentStatus
from usage_billing.db import BaseConnector

from app.deps import get_db, get_invoice_service
from app.errors import require
from app.schemas.common import dump_provided, pagination_params
from app.schemas.invoices import (
    InvoiceCreate,
    InvoicePreview,
    InvoiceUpdate,
    SubscriptionInvoiceCreate,
)
from app.serialize import serialize

router = APIRouter(prefix="/invoices", tags=["invoices"])

DbDep = Annotated[BaseConnector, Depends(get_db)]


def _service(db: BaseConnector, request: Request) -> InvoiceService:
    return get_invoice_service(db, request)


@router.post("", status_code=201)
async def create_invoice(
    body: InvoiceCreate, db: DbDep, request: Request
) -> dict[str, Any]:
    payload = body.model_dump()
    tax_catalog = payload.get("tax_catalog")
    if tax_catalog is not None:
        payload["tax_catalog"] = {
            code: values for code, values in tax_catalog.items()
        }
    return serialize(await _service(db, request).add(**payload))


@router.post("/from-subscription", status_code=201)
async def create_subscription_invoice(
    body: SubscriptionInvoiceCreate, db: DbDep, request: Request
) -> dict[str, Any]:
    return serialize(
        await _service(db, request).create_from_subscription(**body.model_dump())
    )


@router.post("/preview")
async def preview_invoice(
    body: InvoicePreview, db: DbDep, request: Request
) -> dict[str, Any]:
    payload = body.model_dump()
    tax_catalog = payload.get("tax_catalog")
    if tax_catalog is not None:
        payload["tax_catalog"] = {
            code: values for code, values in tax_catalog.items()
        }
    return serialize(await _service(db, request).preview(**payload))


@router.get("")
async def list_invoices(
    db: DbDep,
    request: Request,
    pagination: Annotated[tuple[int, int], Depends(pagination_params)],
    external_customer_id: str | None = Query(default=None),
    status: InvoiceStatus | None = Query(default=None),
    payment_status: PaymentStatus | None = Query(default=None),
) -> dict[str, Any]:
    page, per_page = pagination
    return serialize(
        await _service(db, request).list(
            external_customer_id=external_customer_id,
            status=status,
            payment_status=payment_status,
            page=page,
            per_page=per_page,
        )
    )


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: int, db: DbDep, request: Request
) -> dict[str, Any]:
    invoice = require(
        await _service(db, request).get(invoice_id),
        f"Unknown invoice id: {invoice_id}",
    )
    return serialize(invoice)


@router.patch("/{invoice_id}")
async def update_invoice(
    invoice_id: int, body: InvoiceUpdate, db: DbDep, request: Request
) -> dict[str, Any]:
    return serialize(
        await _service(db, request).update(invoice_id, **dump_provided(body))
    )


@router.post("/{invoice_id}/void")
async def void_invoice(
    invoice_id: int, db: DbDep, request: Request
) -> dict[str, Any]:
    return serialize(await _service(db, request).void(invoice_id))


@router.post("/{invoice_id}/refresh")
async def refresh_invoice(
    invoice_id: int, db: DbDep, request: Request
) -> dict[str, Any]:
    return serialize(await _service(db, request).refresh(invoice_id))


@router.post("/{invoice_id}/finalize")
async def finalize_invoice(
    invoice_id: int, db: DbDep, request: Request
) -> dict[str, Any]:
    return serialize(await _service(db, request).finalize(invoice_id))


@router.post("/{invoice_id}/download")
async def download_invoice(
    invoice_id: int, db: DbDep, request: Request
) -> dict[str, Any]:
    return serialize(await _service(db, request).generate_pdf(invoice_id))


@router.get("/{invoice_id}/file")
async def invoice_file(
    invoice_id: int, db: DbDep, request: Request
) -> Response:
    service = _service(db, request)
    invoice = require(
        await service.get(invoice_id),
        f"Unknown invoice id: {invoice_id}",
    )
    content = service.read_pdf(invoice_id)
    filename = f"{invoice.number or invoice_id}.pdf"
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
