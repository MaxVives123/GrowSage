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

# Named shared-memory DB — all connections in this process share the same DB
TEST_DB_URL = "sqlite:///file:growsage_test?mode=memory&cache=shared&uri=true"


@pytest.fixture(scope="session", autouse=True)
def _set_env():
    """Ensure SECRET_KEY is set for tests and email verification is auto-approved."""
    os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
    os.environ.setdefault("AUTO_VERIFY_EMAIL", "true")


@pytest.fixture(scope="session")
def app():
    """
    FastAPI app wired to an isolated in-memory SQLite test database.
    ChromaDB and OpenAI use real services.
    """
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False, "uri": True},
    )
    Base.metadata.create_all(engine)
    TestFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Override session factory before creating app
    deps._session_factory = TestFactory

    application = create_app(db_url=TEST_DB_URL)
    yield application

    Base.metadata.drop_all(engine)
    engine.dispose()


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
