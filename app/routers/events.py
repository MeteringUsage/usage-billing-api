"""Usage-event ingestion and read endpoints."""

from __future__ import annotations

import json
from typing import Annotated, Any, Mapping

from fastapi import APIRouter, Depends, Query

from usage_billing.db import BaseConnector
from usage_billing.ingestion.core import EventIngestionService
from usage_billing.ingestion.persistence import EventRepository
from usage_billing.ingestion.sdk.models import Event

from app.deps import get_db, get_event_repository, get_ingestion_service
from app.errors import require
from app.schemas.events import EventIngest
from app.serialize import serialize

router = APIRouter(prefix="/events", tags=["events"])

DbDep = Annotated[BaseConnector, Depends(get_db)]


def _ingest(db: BaseConnector) -> EventIngestionService:
    return get_ingestion_service(db)


def _events(db: BaseConnector) -> EventRepository:
    return get_event_repository(db)


def _event_row(row: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(row)
    properties = data.get("properties")
    if isinstance(properties, str):
        data["properties"] = json.loads(properties)
    return data


@router.post("", status_code=201)
async def ingest_event(body: EventIngest, db: DbDep) -> dict[str, Any]:
    result = await _ingest(db).ingest(Event.from_dict(body.model_dump()))
    return serialize(result)


@router.get("")
async def list_events(
    db: DbDep,
    external_subscription_id: str = Query(),
    code: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    rows = await _events(db).list_for_subscription(
        external_subscription_id, code=code
    )
    return [_event_row(row) for row in rows]


@router.get("/{transaction_id}")
async def get_event(transaction_id: str, db: DbDep) -> dict[str, Any]:
    row = require(
        await _events(db).get_by_transaction_id(transaction_id),
        f"Unknown event transaction_id: {transaction_id}",
    )
    return _event_row(row)
