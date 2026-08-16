# usage-billing-api

FastAPI service that exposes the `usage-billing` domain services over HTTP.

## Setup

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

OpenAPI docs: http://127.0.0.1:8000/docs

## Configuration

Environment variables use the `USAGE_BILLING_` prefix:

| Variable | Default | Purpose |
|---|---|---|
| `USAGE_BILLING_DB_BACKEND` | `sql` | `sql` / `sqlite` or `postgres` |
| `USAGE_BILLING_DATABASE` | `usage_billing.db` | SQLite file path |
| `USAGE_BILLING_DATABASE_URL` | unset | Postgres DSN, or `sqlite:///...` |
| `USAGE_BILLING_ENSURE_SCHEMA` | `true` | Create tables on startup |
| `USAGE_BILLING_HOST` | `0.0.0.0` | Bind address |
| `USAGE_BILLING_PORT` | `8000` | Bind port |

## Tests

```bash
pytest
```
