from datetime import datetime, timezone


def _create_metric(client, code="llm_tokens", aggregation="sum", prop="tokens_out"):
    response = client.post(
        "/billable-metrics",
        json={
            "name": code,
            "code": code,
            "metric_type": "metered",
            "aggregation_type": aggregation,
            "aggregate_property": prop,
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_customer(client, external_id="cust-42"):
    response = client.post(
        "/customers",
        json={
            "external_id": external_id,
            "name": "Customer 42",
            "currency": "USD",
            "billing_entity_code": "org-42",
            "taxes": [{"code": "vat", "name": "VAT", "rate": 20}],
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_plan(client, code="ai"):
    response = client.post(
        "/plans",
        json={
            "name": "AI",
            "code": code,
            "interval": "monthly",
            "currency": "USD",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_customer_plan_subscription_invoice_flow(client):
    customer = _create_customer(client)
    plan = _create_plan(client)
    metric = _create_metric(client)

    charge = client.post(
        f"/plans/{plan['code']}/charges",
        json={
            "billable_metric_id": metric["id"],
            "pricing_model": "standard",
            "properties": {"amount": "10"},
        },
    )
    assert charge.status_code == 201
    assert charge.json()["plan_id"] == plan["id"]

    subscription = client.post(
        "/subscriptions",
        json={
            "external_id": "sub-42",
            "customer_id": customer["id"],
            "plan_id": plan["id"],
            "external_customer_id": customer["external_id"],
            "plan_code": plan["code"],
        },
    )
    assert subscription.status_code == 201
    assert subscription.json()["status"] == "active"

    listed = client.get("/subscriptions", params={"external_customer_id": "cust-42"})
    assert listed.status_code == 200
    assert listed.json()["meta"]["total_count"] == 1

    invoice = client.post(
        "/invoices",
        json={
            "external_customer_id": "cust-42",
            "currency": "USD",
            "fees": [
                {
                    "add_on_code": "setup",
                    "units": 1,
                    "unit_amount_cents": 1000,
                }
            ],
        },
    )
    assert invoice.status_code == 201
    invoice_id = invoice.json()["id"]
    assert invoice.json()["total_amount_cents"] > 0

    paid = client.patch(
        f"/invoices/{invoice_id}",
        json={"payment_status": "succeeded"},
    )
    assert paid.status_code == 200
    assert paid.json()["payment_status"] == "succeeded"

    blocked = client.post(f"/invoices/{invoice_id}/void")
    assert blocked.status_code == 400

    terminated = client.post(
        "/subscriptions/sub-42/terminate",
        json={"cancellation_reason": "customer_request"},
    )
    assert terminated.status_code == 200
    assert terminated.json()["status"] == "terminated"


def test_event_ingestion_and_usage(client):
    customer = _create_customer(client)
    plan = _create_plan(client)
    metric = _create_metric(client)

    client.post(
        f"/plans/{plan['code']}/charges",
        json={
            "billable_metric_id": metric["id"],
            "pricing_model": "package",
            "invoice_display_name": "Token packages",
            "properties": {
                "amount": "30",
                "free_units": 100,
                "package_size": 1000,
            },
        },
    )
    client.post(
        "/subscriptions",
        json={
            "external_id": "sub-42",
            "customer_id": customer["id"],
            "plan_id": plan["id"],
            "external_customer_id": customer["external_id"],
            "plan_code": plan["code"],
            "current_billing_period_started_at": "2023-11-01T00:00:00Z",
            "current_billing_period_ending_at": "2023-12-01T00:00:00Z",
        },
    )

    timestamp = int(datetime(2023, 11, 15, tzinfo=timezone.utc).timestamp())
    stored = client.post(
        "/events",
        json={
            "transaction_id": "token-1",
            "external_subscription_id": "sub-42",
            "code": "llm_tokens",
            "timestamp": timestamp,
            "properties": {"tokens_out": 1500},
        },
    )
    assert stored.status_code == 201
    assert stored.json()["status"] == "stored"

    duplicate = client.post(
        "/events",
        json={
            "transaction_id": "token-1",
            "external_subscription_id": "sub-42",
            "code": "llm_tokens",
            "timestamp": timestamp,
            "properties": {"tokens_out": 1500},
        },
    )
    assert duplicate.status_code == 201
    assert duplicate.json()["status"] == "duplicate"

    fetched = client.get("/events/token-1")
    assert fetched.status_code == 200
    assert fetched.json()["code"] == "llm_tokens"

    analytics = client.get(
        "/usage/analytics",
        params={
            "external_customer_id": "cust-42",
            "external_subscription_id": "sub-42",
            "start_of_period_dt": "2023-11-01",
            "end_of_period_dt": "2023-11-30",
        },
    )
    assert analytics.status_code == 200
    usages = analytics.json()["usages"]
    assert usages[0]["billable_metric_code"] == "llm_tokens"
    assert usages[0]["units"] == "1500.0"

    current = client.get(
        "/usage/current",
        params={
            "external_customer_id": "cust-42",
            "external_subscription_id": "sub-42",
        },
    )
    assert current.status_code == 200
    assert current.json()["customer_usage"]["charges_usage"][0]["events_count"] == 1


def test_subscription_invoice_from_usage(client):
    customer = _create_customer(client)
    plan = client.post(
        "/plans",
        json={
            "name": "AI",
            "code": "ai",
            "interval": "monthly",
            "currency": "USD",
            "amount_cents": 1000,
        },
    )
    assert plan.status_code == 201
    metric = _create_metric(client)

    client.post(
        f"/plans/{plan.json()['code']}/charges",
        json={
            "billable_metric_id": metric["id"],
            "pricing_model": "package",
            "invoice_display_name": "Token packages",
            "min_amount_cents": 5000,
            "properties": {
                "amount": "30",
                "free_units": 100,
                "package_size": 1000,
            },
        },
    )
    client.post(
        "/subscriptions",
        json={
            "external_id": "sub-42",
            "customer_id": customer["id"],
            "plan_id": plan.json()["id"],
            "external_customer_id": customer["external_id"],
            "plan_code": plan.json()["code"],
            "current_billing_period_started_at": "2023-11-01T00:00:00Z",
            "current_billing_period_ending_at": "2023-12-01T00:00:00Z",
        },
    )
    timestamp = int(datetime(2023, 11, 15, tzinfo=timezone.utc).timestamp())
    client.post(
        "/events",
        json={
            "transaction_id": "token-1",
            "external_subscription_id": "sub-42",
            "code": "llm_tokens",
            "timestamp": timestamp,
            "properties": {"tokens_out": 1500},
        },
    )

    invoice = client.post(
        "/invoices/from-subscription",
        json={
            "external_customer_id": "cust-42",
            "external_subscription_id": "sub-42",
        },
    )
    assert invoice.status_code == 201
    body = invoice.json()
    assert body["invoice_type"] == "subscription"
    # package: ceil((1500-100)/1000)*30 = 2*30 = 6000 cents; min 5000 so no true-up
    # plus plan fee 1000
    assert body["fees_amount_cents"] == 7000
    assert body["taxes_amount_cents"] == 1400
    assert body["total_amount_cents"] == 8400
    assert body["subscriptions"][0]["external_id"] == "sub-42"
    item_types = {fee["item_type"] for fee in body["fees"]}
    assert item_types == {"subscription", "charge"}

    duplicate = client.post(
        "/invoices/from-subscription",
        json={
            "external_customer_id": "cust-42",
            "external_subscription_id": "sub-42",
        },
    )
    assert duplicate.status_code == 400

    preview = client.post(
        "/invoices/preview",
        json={
            "external_customer_id": "cust-42",
            "external_subscription_id": "sub-42",
        },
    )
    assert preview.status_code == 200
    assert preview.json()["id"] is None
    assert preview.json()["number"] == "PREVIEW"
    assert preview.json()["fees_amount_cents"] == 7000

    downloaded = client.post(f"/invoices/{body['id']}/download")
    assert downloaded.status_code == 200
    assert downloaded.json()["file_url"] == f"/invoices/{body['id']}/file"
    pdf = client.get(f"/invoices/{body['id']}/file")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content.startswith(b"%PDF")


def test_usage_check_limit(client):
    customer = _create_customer(client, "cust-limit")
    plan = _create_plan(client, "capped")
    metric = _create_metric(client, "api_calls", "sum", "calls")

    charge = client.post(
        f"/plans/{plan['code']}/charges",
        json={
            "billable_metric_id": metric["id"],
            "pricing_model": "standard",
            "properties": {"amount": "1"},
            "included_units": 10,
        },
    )
    assert charge.status_code == 201
    assert charge.json()["included_units"] == 10

    client.post(
        "/subscriptions",
        json={
            "external_id": "sub-limit",
            "customer_id": customer["id"],
            "plan_id": plan["id"],
            "external_customer_id": customer["external_id"],
            "plan_code": plan["code"],
            "current_billing_period_started_at": "2023-11-01T00:00:00Z",
            "current_billing_period_ending_at": "2023-12-01T00:00:00Z",
        },
    )
    timestamp = int(datetime(2023, 11, 15, tzinfo=timezone.utc).timestamp())
    client.post(
        "/events",
        json={
            "transaction_id": "call-1",
            "external_subscription_id": "sub-limit",
            "code": "api_calls",
            "timestamp": timestamp,
            "properties": {"calls": 6},
        },
    )

    allowed = client.post(
        "/usage/check",
        json={
            "external_customer_id": "cust-limit",
            "external_subscription_id": "sub-limit",
            "code": "api_calls",
            "units": 4,
        },
    )
    assert allowed.status_code == 200
    assert allowed.json()["allowed"] is True
    assert allowed.json()["out_of_plan"] is False
    assert allowed.json()["remaining_units"] == "4.0"

    overage = client.post(
        "/usage/check",
        json={
            "external_customer_id": "cust-limit",
            "external_subscription_id": "sub-limit",
            "code": "api_calls",
            "units": 5,
        },
    )
    assert overage.status_code == 200
    assert overage.json()["allowed"] is True
    assert overage.json()["out_of_plan"] is True
    assert "charged" in overage.json()["message"]

    stored = client.post(
        "/events",
        json={
            "transaction_id": "call-2",
            "external_subscription_id": "sub-limit",
            "code": "api_calls",
            "timestamp": timestamp,
            "properties": {"calls": 4},
        },
    )
    assert stored.status_code == 201
    assert stored.json()["status"] == "stored"
    assert stored.json()["out_of_plan"] is False

    billed = client.post(
        "/events",
        json={
            "transaction_id": "call-3",
            "external_subscription_id": "sub-limit",
            "code": "api_calls",
            "timestamp": timestamp,
            "properties": {"calls": 2},
        },
    )
    assert billed.status_code == 201
    assert billed.json()["status"] == "stored"
    assert billed.json()["out_of_plan"] is True
    assert "charged" in billed.json()["message"]

    forced = client.post(
        "/usage/check",
        json={
            "external_customer_id": "cust-limit",
            "external_subscription_id": "sub-limit",
            "code": "api_calls",
            "units": 1,
            "block_overage": True,
        },
    )
    assert forced.status_code == 403
