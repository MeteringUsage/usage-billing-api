"""Customer request bodies."""

from __future__ import annotations

from typing import Any

from usage_billing.customer import AccountType, FinalizeZeroAmountInvoice

from app.schemas.common import ApiModel


class CustomerCreate(ApiModel):
    external_id: str
    name: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    phone: str | None = None
    legal_name: str | None = None
    legal_number: str | None = None
    tax_identification_number: str | None = None
    currency: str | None = None
    timezone: str | None = None
    applicable_timezone: str | None = None
    billing_entity_code: str | None = None
    account_type: AccountType = AccountType.CUSTOMER
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    zipcode: str | None = None
    url: str | None = None
    logo_url: str | None = None
    net_payment_term: int | None = None
    finalize_zero_amount_invoice: FinalizeZeroAmountInvoice = (
        FinalizeZeroAmountInvoice.INHERIT
    )
    skip_invoice_custom_sections: bool = False
    sequential_id: int | None = None
    slug: str | None = None
    billing_configuration: dict[str, Any] | None = None
    shipping_address: dict[str, Any] | None = None
    metadata: list[dict[str, Any]] | None = None
    integration_customers: list[dict[str, Any]] | None = None
    taxes: list[dict[str, Any]] | None = None
    applicable_invoice_custom_sections: list[dict[str, Any]] | None = None
    error_details: list[dict[str, Any]] | None = None


class CustomerUpdate(ApiModel):
    name: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    phone: str | None = None
    legal_name: str | None = None
    legal_number: str | None = None
    tax_identification_number: str | None = None
    currency: str | None = None
    timezone: str | None = None
    applicable_timezone: str | None = None
    billing_entity_code: str | None = None
    account_type: AccountType | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    zipcode: str | None = None
    url: str | None = None
    logo_url: str | None = None
    net_payment_term: int | None = None
    finalize_zero_amount_invoice: FinalizeZeroAmountInvoice | None = None
    skip_invoice_custom_sections: bool | None = None
    billing_configuration: dict[str, Any] | None = None
    shipping_address: dict[str, Any] | None = None
    metadata: list[dict[str, Any]] | None = None
    integration_customers: list[dict[str, Any]] | None = None
    taxes: list[dict[str, Any]] | None = None
    applicable_invoice_custom_sections: list[dict[str, Any]] | None = None
    error_details: list[dict[str, Any]] | None = None
