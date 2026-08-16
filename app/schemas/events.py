"""Usage-event request bodies."""

from __future__ import annotations

from typing import Any

from app.schemas.common import ApiModel


class EventIngest(ApiModel):
    transaction_id: str
    external_subscription_id: str
    code: str
    timestamp: int
    properties: dict[str, Any] = {}
