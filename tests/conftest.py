from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    settings = Settings(
        db_backend="sql",
        database=str(tmp_path / "usage_billing.db"),
        invoice_files=str(tmp_path / "invoices"),
        ensure_schema=True,
    )
    with TestClient(create_app(settings)) as test_client:
        yield test_client
