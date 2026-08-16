"""Billable metric request bodies."""

from __future__ import annotations

from usage_billing.metering import AggregationType, MetricType

from app.schemas.common import ApiModel


class BillableMetricCreate(ApiModel):
    name: str
    code: str
    metric_type: MetricType
    aggregation_type: AggregationType
    description: str | None = None
    aggregate_property: str | None = None


class BillableMetricUpdate(ApiModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    metric_type: MetricType | None = None
    aggregation_type: AggregationType | None = None
    aggregate_property: str | None = None
