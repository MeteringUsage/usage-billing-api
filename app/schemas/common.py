"""Shared request helpers."""

from __future__ import annotations

from typing import Any

from fastapi import Query
from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def pagination_params(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> tuple[int, int]:
    return page, per_page


def dump_provided(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(exclude_unset=True)
