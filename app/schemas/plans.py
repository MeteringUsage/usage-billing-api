"""Plan and plan-charge request bodies."""

from __future__ import annotations

from typing import Any

from usage_billing.plan import PayType, PlanInterval, PricingModel

from app.schemas.common import ApiModel


class RecurringChargeIn(ApiModel):
    name: str
    interval: PlanInterval
    amount: float
    pay_type: PayType


class PlanCreate(ApiModel):
    name: str
    code: str
    interval: PlanInterval
    currency: str
    amount_cents: int = 0
    invoice_display_name: str | None = None
    description: str | None = None
    trial_period: int | None = None
    pay_in_advance: bool = False
    bill_charges_monthly: bool | None = None
    bill_fixed_charges_monthly: bool | None = None
    recurring_charges: list[RecurringChargeIn] | None = None
    minimum_commitment: dict[str, Any] | None = None
    fixed_charges: list[dict[str, Any]] | None = None
    taxes: list[dict[str, Any]] | None = None
    usage_thresholds: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


class PlanUpdate(ApiModel):
    name: str | None = None
    code: str | None = None
    interval: PlanInterval | None = None
    currency: str | None = None
    amount_cents: int | None = None
    invoice_display_name: str | None = None
    description: str | None = None
    trial_period: int | None = None
    pay_in_advance: bool | None = None
    bill_charges_monthly: bool | None = None
    bill_fixed_charges_monthly: bool | None = None
    recurring_charges: list[RecurringChargeIn] | None = None
    minimum_commitment: dict[str, Any] | None = None
    fixed_charges: list[dict[str, Any]] | None = None
    taxes: list[dict[str, Any]] | None = None
    usage_thresholds: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


class PlanChargeCreate(ApiModel):
    billable_metric_id: int
    pricing_model: PricingModel
    properties: dict[str, Any] | None = None
    filters: list[dict[str, Any]] | None = None
    invoice_display_name: str | None = None
    pay_in_advance: bool = False
    prorated: bool = False
    min_amount_cents: int = 0
    included_units: int | None = None
    block_overage: bool = False
    exclude_included_units: bool = True


class PlanChargeUpdate(ApiModel):
    billable_metric_id: int | None = None
    pricing_model: PricingModel | None = None
    properties: dict[str, Any] | None = None
    filters: list[dict[str, Any]] | None = None
    invoice_display_name: str | None = None
    pay_in_advance: bool | None = None
    prorated: bool | None = None
    min_amount_cents: int | None = None
    included_units: int | None = None
    block_overage: bool | None = None
    exclude_included_units: bool | None = None
