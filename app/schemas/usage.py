"""Usage request bodies."""

from __future__ import annotations

from decimal import Decimal

from app.schemas.common import ApiModel


class UsageCheckRequest(ApiModel):
    external_customer_id: str
    external_subscription_id: str
    code: str
    units: Decimal
    block_overage: bool | None = None
