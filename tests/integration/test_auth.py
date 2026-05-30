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


def test_register_short_password_returns_422(client):
    res = client.post(
        "/auth/register",
        json={"email": "bob@growsage.com", "password": "short"},
    )
    assert res.status_code == 422


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


def test_login_wrong_password_returns_401(client):
    client.post(
        "/auth/register",
        json={"email": "dave@growsage.com", "password": "correctpass1"},
    )
    res = client.post(
        "/auth/login",
        json={"email": "dave@growsage.com", "password": "wrongpassword"},
    )
    assert res.status_code == 401


def test_login_unknown_email_returns_401(client):
    res = client.post(
        "/auth/login",
        json={"email": "nobody@growsage.com", "password": "doesntmatter"},
    )
    assert res.status_code == 401


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
