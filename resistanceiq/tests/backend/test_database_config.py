import pytest
from sqlalchemy import create_engine
from app.core.database import normalize_database_url, engine, Base


def test_normalize_database_url_variations():
    # 1. postgres:// -> postgresql+psycopg://
    assert normalize_database_url("postgres://user:pwd@db.host.com:5432/db") == "postgresql+psycopg://user:pwd@db.host.com:5432/db"

    # 2. postgresql:// -> postgresql+psycopg://
    assert normalize_database_url("postgresql://user:pwd@db.host.com:5432/db") == "postgresql+psycopg://user:pwd@db.host.com:5432/db"

    # 3. Explicit postgresql+psycopg:// remains unchanged
    assert normalize_database_url("postgresql+psycopg://user:pwd@db.host.com:5432/db") == "postgresql+psycopg://user:pwd@db.host.com:5432/db"

    # 4. Explicit postgresql+psycopg2:// remains unchanged
    assert normalize_database_url("postgresql+psycopg2://user:pwd@db.host.com:5432/db") == "postgresql+psycopg2://user:pwd@db.host.com:5432/db"

    # 5. SQLite remains unchanged
    assert normalize_database_url("sqlite:///resistanceiq_dev.db") == "sqlite:///resistanceiq_dev.db"
    assert normalize_database_url("sqlite:///:memory:") == "sqlite:///:memory:"

    # 6. None or empty string handles gracefully
    assert normalize_database_url("") == ""
    assert normalize_database_url(None) is None


def test_psycopg3_driver_import_and_dialect():
    # Verify psycopg (Psycopg 3) can be imported
    import psycopg
    assert hasattr(psycopg, "__version__")
    assert len(psycopg.__version__) > 0

    # Verify SQLAlchemy can create engine using postgresql+psycopg without error
    test_db_url = "postgresql+psycopg://test_user:test_pwd@localhost:5432/test_db"
    dummy_engine = create_engine(test_db_url)
    assert dummy_engine.dialect.name == "postgresql"
    assert dummy_engine.dialect.driver == "psycopg"


def test_health_endpoints_without_database_access(client):
    # Root endpoint verification
    root_res = client.get("/")
    assert root_res.status_code == 200
    root_data = root_res.json()
    assert root_data["status"] == "ONLINE"

    # Health endpoint verification (Render health check path)
    health_res = client.get("/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["status"] == "HEALTHY"
    assert "service" in health_data
    assert "version" in health_data
