# usage-billing-api

FastAPI HTTP service for the [`usage-billing`](https://github.com/MeteringUsage/usage-billing) Python package.

It exposes metrics, plans, customers, subscriptions, usage events, usage analytics, and invoices over REST. Domain logic lives in `usage-billing`; this repo is the HTTP layer, request validation, and error mapping.

Interactive OpenAPI docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Features

- CRUD for billable metrics, plans, plan charges, and customers
- Subscription create, update, list, and terminate
- Direct event ingestion and lookup by `transaction_id`
- Current-period and analytics usage, plus overage checks
- One-off invoices, subscription invoices, preview, void, refresh, finalize, and PDF download
- SQLite by default; PostgreSQL via optional extra
- Schema bootstrap on startup (`USAGE_BILLING_ENSURE_SCHEMA`)

## Layout

```
usage-billing-api/
  app/
    main.py            # FastAPI factory, CORS, routers, /health
    config.py          # USAGE_BILLING_* settings
    deps.py            # DB connector and domain services
    errors.py          # domain errors → HTTP status codes
    serialize.py       # dataclass / pagination serialization
    routers/           # HTTP endpoints
    schemas/           # Pydantic request bodies
  tests/
  pyproject.toml
  README.md
```

This package depends on the sibling checkout:

```
../usage-billing
```

Install `usage-billing` first, or keep both repos as siblings so the `file:../usage-billing` dependency in `pyproject.toml` resolves.

## Setup

Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

PostgreSQL:

```bash
pip install -e ".[dev,postgres]"
```

## Run

```bash
uvicorn app.main:app --reload
```

Or:

```bash
python -m app
```

The CLI entrypoint `usage-billing-api` also starts uvicorn with host/port from settings.

| URL | Description |
|---|---|
| http://127.0.0.1:8000/health | Liveness |
| http://127.0.0.1:8000/docs | Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc |

On startup, if `USAGE_BILLING_ENSURE_SCHEMA` is true (default), the service creates tables for customers, metrics, plans, charges, subscriptions, events, invoices, and usage.

## Configuration

Settings are read from environment variables (prefix `USAGE_BILLING_`) or a `.env` file.

| Variable | Default | Purpose |
|---|---|---|
| `USAGE_BILLING_DB_BACKEND` | `sql` | `sql` / `sqlite` or `postgres` / `postgresql` |
| `USAGE_BILLING_DATABASE` | `usage_billing.db` | SQLite file path when no URL is set |
| `USAGE_BILLING_DATABASE_URL` | unset | Postgres DSN, or `sqlite:///path/to.db` |
| `USAGE_BILLING_ENSURE_SCHEMA` | `true` | Create tables on startup |
| `USAGE_BILLING_HOST` | `0.0.0.0` | Bind address |
| `USAGE_BILLING_PORT` | `8000` | Bind port |
| `USAGE_BILLING_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allowed origins |
| `USAGE_BILLING_INVOICE_FILES` | `invoice_files` | Directory for generated invoice PDFs |

Examples:

```bash
# SQLite (default)
export USAGE_BILLING_DB_BACKEND=sql
export USAGE_BILLING_DATABASE=usage_billing.db

# PostgreSQL
export USAGE_BILLING_DB_BACKEND=postgres
export USAGE_BILLING_DATABASE_URL=postgresql://user:pass@localhost:5432/usage_billing
```

If `USAGE_BILLING_DATABASE_URL` is set, it wins: `postgres://` / `postgresql://` use the Postgres connector; `sqlite:///` uses SQLite.

## API

List endpoints support `page` (default 1) and `per_page` (default 20, max 100) and return `{ "data": [...], "meta": { ... } }`.

Unknown extra JSON fields are rejected (`extra="forbid"`).

### Health

| Method | Path |
|---|---|
| `GET` | `/health` |

### Billable metrics

| Method | Path |
|---|---|
| `POST` | `/billable-metrics` |
| `GET` | `/billable-metrics` |
| `GET` | `/billable-metrics/{code}` |
| `PATCH` | `/billable-metrics/{code}` |
| `DELETE` | `/billable-metrics/{code}` |

### Plans and charges

| Method | Path |
|---|---|
| `POST` | `/plans` |
| `GET` | `/plans` |
| `GET` | `/plans/{code}` |
| `PATCH` | `/plans/{code}` |
| `DELETE` | `/plans/{code}` |
| `POST` | `/plans/{code}/charges` |
| `GET` | `/plans/{code}/charges` |
| `GET` | `/plans/{code}/charges/{charge_id}` |
| `PATCH` | `/plans/{code}/charges/{charge_id}` |
| `DELETE` | `/plans/{code}/charges/{charge_id}` |

### Customers

| Method | Path |
|---|---|
| `POST` | `/customers` |
| `GET` | `/customers` |
| `GET` | `/customers/{external_id}` |
| `PATCH` | `/customers/{external_id}` |
| `DELETE` | `/customers/{external_id}` |

### Subscriptions

| Method | Path | Notes |
|---|---|---|
| `POST` | `/subscriptions` | |
| `GET` | `/subscriptions` | Filter: `external_customer_id`, `status` |
| `GET` | `/subscriptions/{external_id}` | |
| `PATCH` | `/subscriptions/{external_id}` | |
| `POST` | `/subscriptions/{external_id}/terminate` | |

### Events

| Method | Path | Notes |
|---|---|---|
| `POST` | `/events` | Ingest one event (`transaction_id` is the idempotency key) |
| `GET` | `/events` | Required: `external_subscription_id`. Optional: `code` |
| `GET` | `/events/{transaction_id}` | |

### Usage

| Method | Path | Notes |
|---|---|---|
| `GET` | `/usage/analytics` | Required: `external_customer_id`, `external_subscription_id`, `start_of_period_dt`, `end_of_period_dt` |
| `GET` | `/usage/current` | Required: `external_customer_id`, `external_subscription_id`. Optional: `at` |
| `POST` | `/usage/check` | Check whether additional units would exceed a charge limit |

### Invoices

| Method | Path | Notes |
|---|---|---|
| `POST` | `/invoices` | One-off invoice with explicit fees |
| `POST` | `/invoices/from-subscription` | Invoice from current subscription usage |
| `POST` | `/invoices/preview` | Calculate without persisting |
| `GET` | `/invoices` | Filter: `external_customer_id`, `status`, `payment_status` |
| `GET` | `/invoices/{invoice_id}` | |
| `PATCH` | `/invoices/{invoice_id}` | `payment_status`, `metadata` |
| `POST` | `/invoices/{invoice_id}/void` | |
| `POST` | `/invoices/{invoice_id}/refresh` | |
| `POST` | `/invoices/{invoice_id}/finalize` | |
| `POST` | `/invoices/{invoice_id}/download` | Generate PDF and return invoice metadata |
| `GET` | `/invoices/{invoice_id}/file` | Download PDF (`application/pdf`) |

## Example flow

```bash
# 1. Billable metric
curl -s -X POST http://127.0.0.1:8000/billable-metrics \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "LLM tokens",
    "code": "llm_tokens",
    "metric_type": "metered",
    "aggregation_type": "sum",
    "aggregate_property": "tokens_out"
  }'

# 2. Plan
curl -s -X POST http://127.0.0.1:8000/plans \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "AI",
    "code": "ai",
    "interval": "monthly",
    "currency": "USD"
  }'

# 3. Charge on the plan (use billable_metric_id from step 1)
curl -s -X POST http://127.0.0.1:8000/plans/ai/charges \
  -H 'Content-Type: application/json' \
  -d '{
    "billable_metric_id": 1,
    "pricing_model": "standard",
    "properties": {"amount": "10"}
  }'

# 4. Customer
curl -s -X POST http://127.0.0.1:8000/customers \
  -H 'Content-Type: application/json' \
  -d '{
    "external_id": "cust-42",
    "name": "Customer 42",
    "currency": "USD",
    "billing_entity_code": "org-42"
  }'

# 5. Subscription (use customer_id and plan_id from earlier responses)
curl -s -X POST http://127.0.0.1:8000/subscriptions \
  -H 'Content-Type: application/json' \
  -d '{
    "external_id": "sub-42",
    "customer_id": 1,
    "plan_id": 1,
    "external_customer_id": "cust-42",
    "plan_code": "ai"
  }'

# 6. Ingest usage
curl -s -X POST http://127.0.0.1:8000/events \
  -H 'Content-Type: application/json' \
  -d '{
    "transaction_id": "evt_001",
    "external_subscription_id": "sub-42",
    "code": "llm_tokens",
    "timestamp": 1710421740,
    "properties": {"tokens_out": 1500, "model": "gpt-4"}
  }'

# 7. Current usage
curl -s 'http://127.0.0.1:8000/usage/current?external_customer_id=cust-42&external_subscription_id=sub-42'

# 8. Invoice from the subscription
curl -s -X POST http://127.0.0.1:8000/invoices/from-subscription \
  -H 'Content-Type: application/json' \
  -d '{
    "external_customer_id": "cust-42",
    "external_subscription_id": "sub-42"
  }'
```

## Errors

| HTTP | When |
|---|---|
| `400` | `ValueError` from domain validation |
| `403` | Usage limit exceeded (`LimitExceededError`) |
| `404` | Missing resource (`NotFoundError`) |
| `409` | Unique / foreign-key conflicts |
| `422` | Request body validation |
| `500` | Unhandled server error |

Error bodies are `{"detail": "..."}`.

Each request opens a database connection, commits on success, and rolls back on failure.

## Tests

```bash
pytest
```

Tests use `TestClient` with a temporary SQLite database and invoice directory. They do not need a running server.

## Related

- Domain library: [MeteringUsage/usage-billing](https://github.com/MeteringUsage/usage-billing)
- Domain docs in that repo: getting started, plans, subscriptions, billing, and the event SDK
