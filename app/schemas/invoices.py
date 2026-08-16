"""Invoice request bodies."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from usage_billing.billing import InvoiceStatus, InvoiceType, PaymentStatus

from app.schemas.common import ApiModel


class InvoiceFeeIn(ApiModel):
    add_on_code: str
    units: float
    unit_amount_cents: int
    description: str | None = None
    tax_codes: list[str] = []
    invoice_display_name: str | None = None


class TaxDefinitionIn(ApiModel):
    code: str
    name: str
    rate: float
    description: str | None = None


class InvoiceCreate(ApiModel):
    external_customer_id: str
    currency: str
    fees: list[InvoiceFeeIn]
    invoice_type: InvoiceType = InvoiceType.ONE_OFF
    status: InvoiceStatus = InvoiceStatus.FINALIZED
    payment_status: PaymentStatus = PaymentStatus.PENDING
    tax_catalog: dict[str, TaxDefinitionIn] | None = None
    coupons_amount_cents: int = 0
    credit_notes_amount_cents: int = 0
    prepaid_credit_amount_cents: int = 0
    progressive_billing_credit_amount_cents: int = 0
    purchase_order_number: str | None = None
    billing_entity_code: str | None = None
    metadata: list[dict[str, Any]] | None = None
    net_payment_term: int | None = None


class SubscriptionInvoiceCreate(ApiModel):
    external_customer_id: str
    external_subscription_id: str
    at: datetime | None = None
    status: InvoiceStatus = InvoiceStatus.FINALIZED
    payment_status: PaymentStatus | None = None
    coupons_amount_cents: int = 0
    credit_notes_amount_cents: int = 0
    prepaid_credit_amount_cents: int = 0
    progressive_billing_credit_amount_cents: int = 0
    purchase_order_number: str | None = None
    billing_entity_code: str | None = None
    metadata: list[dict[str, Any]] | None = None
    net_payment_term: int | None = None


class InvoicePreview(ApiModel):
    external_customer_id: str
    external_subscription_id: str | None = None
    currency: str | None = None
    fees: list[InvoiceFeeIn] | None = None
    at: datetime | None = None
    invoice_type: InvoiceType = InvoiceType.ONE_OFF
    tax_catalog: dict[str, TaxDefinitionIn] | None = None
    coupons_amount_cents: int = 0
    credit_notes_amount_cents: int = 0
    prepaid_credit_amount_cents: int = 0
    progressive_billing_credit_amount_cents: int = 0
    purchase_order_number: str | None = None
    billing_entity_code: str | None = None
    metadata: list[dict[str, Any]] | None = None
    net_payment_term: int | None = None


class InvoiceUpdate(ApiModel):
    payment_status: PaymentStatus | None = None
    metadata: list[dict[str, Any]] | None = None
