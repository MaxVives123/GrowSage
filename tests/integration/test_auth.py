"""
Integration tests — Auth endpoints.
No mocks: real SQLite DB, real bcrypt, real JWT.
"""


def test_register_returns_201_with_user_data(client):
    res = client.post(
        "/auth/register",
        json={"email": "alice@growsage.com", "password": "securepass1"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "alice@growsage.com"
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data  # never leak password


def test_register_duplicate_email_returns_409(client):
    payload = {"email": "duplicate@growsage.com", "password": "securepass1"}
    client.post("/auth/register", json=payload)
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 409
    assert "already registered" in res.json()["detail"].lower()


def test_register_short_password_returns_422(client):
    res = client.post(
        "/auth/register",
        json={"email": "bob@growsage.com", "password": "short"},
    )
    assert res.status_code == 422


def test_register_blank_password_returns_422(client):
    """Whitespace-only passwords are rejected."""
    res = client.post(
        "/auth/register",
        json={"email": "blank@growsage.com", "password": "        "},
    )
    assert res.status_code == 422


def test_register_invalid_email_returns_422(client):
    """Malformed email addresses are rejected before hitting the DB."""
    for bad_email in ["notanemail", "missing@dot", "@nodomain.com", "spaces @x.com"]:
        res = client.post(
            "/auth/register",
            json={"email": bad_email, "password": "validpass1"},
        )
        assert res.status_code == 422, f"Expected 422 for email: {bad_email!r}"


def test_register_email_is_normalized_to_lowercase(client):
    """Emails are stored in lowercase regardless of what the user types."""
    res = client.post(
        "/auth/register",
        json={"email": "MixedCase@GrowSage.COM", "password": "validpass1"},
    )
    assert res.status_code == 201
    assert res.json()["email"] == "mixedcase@growsage.com"


def test_login_returns_bearer_token(client):
    client.post(
        "/auth/register",
        json={"email": "carol@growsage.com", "password": "mypassword1"},
    )
    res = client.post(
        "/auth/login",
        json={"email": "carol@growsage.com", "password": "mypassword1"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # JWT has three dot-separated segments
    assert len(data["access_token"].split(".")) == 3


def test_login_is_case_insensitive(client):
    """Logging in with uppercase email works when account was registered in lowercase."""
    client.post(
        "/auth/register",
        json={"email": "casetest@growsage.com", "password": "mypassword1"},
    )
    res = client.post(
        "/auth/login",
        json={"email": "CASETEST@GROWSAGE.COM", "password": "mypassword1"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password_returns_401_with_message(client):
    client.post(
        "/auth/register",
        json={"email": "dave@growsage.com", "password": "correctpass1"},
    )
    res = client.post(
        "/auth/login",
        json={"email": "dave@growsage.com", "password": "wrongpassword"},
    )
    assert res.status_code == 401
    assert "invalid" in res.json()["detail"].lower()


def test_login_unknown_email_returns_401_with_message(client):
    res = client.post(
        "/auth/login",
        json={"email": "nobody@growsage.com", "password": "doesntmatter"},
    )
    assert res.status_code == 401
    # Generic message — does not reveal whether the email exists (anti-enumeration)
    assert "invalid" in res.json()["detail"].lower()


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register_returns_email_verified_false_without_auto_verify(client):
    """When AUTO_VERIFY_EMAIL is off, registration returns email_verified=False."""
    import os
    old = os.environ.get("AUTO_VERIFY_EMAIL")
    os.environ["AUTO_VERIFY_EMAIL"] = "false"
    try:
        res = client.post(
            "/auth/register",
            json={"email": "notauto@growsage.com", "password": "testpass123"},
        )
        assert res.status_code == 201
        assert res.json()["email_verified"] is False
    finally:
        if old is not None:
            os.environ["AUTO_VERIFY_EMAIL"] = old
        else:
            os.environ["AUTO_VERIFY_EMAIL"] = "true"


def test_auto_verified_user_has_email_verified_true(client):
    """With AUTO_VERIFY_EMAIL=true (set in conftest), registration auto-verifies."""
    res = client.post(
        "/auth/register",
        json={"email": "autoverified@growsage.com", "password": "testpass123"},
    )
    assert res.status_code == 201
    assert res.json()["email_verified"] is True


def test_unverified_user_cannot_chat(client):
    """Unverified users get 403 UNVERIFIED_EMAIL when trying to chat."""
    # Register and then manually mark as unverified in the DB
    client.post("/auth/register", json={"email": "willblock@growsage.com", "password": "testpass123"})

    from src.infrastructure.database import UserORM
    from src.api import deps
    db = deps.get_session_factory()()
    try:
        user = db.query(UserORM).filter(UserORM.email == "willblock@growsage.com").first()
        if user:
            user.email_verified = False
            db.commit()
    finally:
        db.close()

    login = client.post("/auth/login", json={"email": "willblock@growsage.com", "password": "testpass123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    res = client.post("/chat", json={"question": "test"}, headers=headers)
    assert res.status_code == 403
    assert res.json()["detail"] == "UNVERIFIED_EMAIL"


def test_verify_email_with_invalid_token_returns_redirect(client):
    """Invalid tokens redirect to frontend with ?verified=error."""
    res = client.get("/auth/verify/invalid-token-xyz", follow_redirects=False)
    assert res.status_code == 302
    assert "verified=error" in res.headers["location"]
