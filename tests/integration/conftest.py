"""
Integration test fixtures.

Uses:
- Isolated SQLite DB (in-memory per session)
- Real ChromaDB (existing 'botanica_huerto' collection, read-only)
- Real OpenAI API (costs pennies per full run)
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import create_app
from src.api import deps
from src.infrastructure.database import Base

TEST_DB_URL = "sqlite:///./test_growsage.db"


@pytest.fixture(scope="session", autouse=True)
def _set_env():
    """Ensure SECRET_KEY is set for tests."""
    os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")


@pytest.fixture(scope="session")
def app():
    """
    FastAPI app wired to an isolated SQLite test database.
    ChromaDB and OpenAI use real services.
    """
    # Clean up any leftover DB from previous runs
    if os.path.exists("test_growsage.db"):
        os.remove("test_growsage.db")

    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Override session factory before creating app
    deps._session_factory = TestFactory

    application = create_app(db_url=TEST_DB_URL)
    yield application

    # Teardown — dispose connections before removing file (Windows file locking)
    Base.metadata.drop_all(engine)
    engine.dispose()
    try:
        if os.path.exists("test_growsage.db"):
            os.remove("test_growsage.db")
    except PermissionError:
        pass  # Windows: file still locked; cleanup on next run


@pytest.fixture(scope="session")
def client(app):
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_headers(client):
    """Register a test user once and return its Bearer headers."""
    client.post(
        "/auth/register",
        json={"email": "integration@growsage.com", "password": "testpass123"},
    )
    res = client.post(
        "/auth/login",
        json={"email": "integration@growsage.com", "password": "testpass123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
