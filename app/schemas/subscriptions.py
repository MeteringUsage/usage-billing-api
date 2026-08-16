"""Subscription request bodies."""

from __future__ import annotations

from typing import Any

from usage_billing.subscription import (
    BillingTime,
    CancellationReason,
    OnTerminationCreditNote,
    OnTerminationInvoice,
    SubscriptionStatus,
)

from app.schemas.common import ApiModel


class SubscriptionCreate(ApiModel):
    external_id: str
    customer_id: int
    plan_id: int
    external_customer_id: str | None = None
    plan_code: str | None = None
    name: str | None = None
    billing_time: BillingTime = BillingTime.ANNIVERSARY
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    billing_entity_code: str | None = None
    plan_amount_cents: int | None = None
    plan_amount_currency: str | None = None
    previous_plan_code: str | None = None
    next_plan_code: str | None = None
    downgrade_plan_date: str | None = None
    started_at: str | None = None
    ending_at: str | None = None
    subscription_at: str | None = None
    canceled_at: str | None = None
    terminated_at: str | None = None
    trial_ended_at: str | None = None
    activated_at: str | None = None
    current_billing_period_started_at: str | None = None
    current_billing_period_ending_at: str | None = None
    on_termination_credit_note: OnTerminationCreditNote | None = None
    on_termination_invoice: OnTerminationInvoice | None = None
    cancellation_reason: CancellationReason | None = None
    consolidate_invoice: bool = False
    purchase_order_number: str | None = None
    payment_method: dict[str, Any] | None = None
    applied_invoice_custom_sections: list[dict[str, Any]] | None = None
    activation_rules: list[dict[str, Any]] | None = None
    applicable_usage_thresholds: list[dict[str, Any]] | None = None
    plan_snapshot: dict[str, Any] | None = None


class SubscriptionUpdate(ApiModel):
    name: str | None = None
    ending_at: str | None = None
    subscription_at: str | None = None
    billing_entity_code: str | None = None
    consolidate_invoice: bool | None = None
    purchase_order_number: str | None = None
    payment_method: dict[str, Any] | None = None
    on_termination_credit_note: OnTerminationCreditNote | None = None
    on_termination_invoice: OnTerminationInvoice | None = None


class SubscriptionTerminate(ApiModel):
    on_termination_credit_note: OnTerminationCreditNote | None = None
    on_termination_invoice: OnTerminationInvoice | None = None
    cancellation_reason: CancellationReason | None = None
    terminated_at: str | None = None
