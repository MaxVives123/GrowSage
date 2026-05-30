"""
Integration tests — Chat endpoint.
No mocks: real ChromaDB (botanica_huerto) + real OpenAI API.
Tests verify structure and properties, not exact LLM output (non-deterministic).
"""
import os


def test_chat_without_token_returns_403(client):
    """Unauthenticated requests are rejected before hitting the LLM."""
    res = client.post("/chat", json={"question": "How do I grow tomatoes?"})
    assert res.status_code == 403


def test_chat_with_invalid_token_returns_401(client):
    res = client.post(
        "/chat",
        json={"question": "How do I grow tomatoes?"},
        headers={"Authorization": "Bearer this.is.invalid"},
    )
    assert res.status_code == 401


def test_chat_empty_question_returns_422(client, auth_headers):
    """Pydantic validator rejects whitespace-only questions."""
    res = client.post("/chat", json={"question": "   "}, headers=auth_headers)
    assert res.status_code == 422


def test_chat_returns_answer_and_sources(client, auth_headers):
    """Full RAG flow: real retrieval + real LLM generation."""
    res = client.post(
        "/chat",
        json={"question": "When should I transplant tomato seedlings?"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert "answer" in data
    assert len(data["answer"]) > 50, "Answer is too short to be meaningful"

    assert "sources" in data
    assert len(data["sources"]) >= 1, "At least one source should be returned"

    for source in data["sources"]:
        assert "name" in source
        assert "page" in source
        assert source["name"]  # not empty


def test_chat_spanish_question_returns_spanish_answer(client, auth_headers):
    res = client.post(
        "/chat",
        json={"question": "¿Cómo hacer compost en casa paso a paso?"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    answer = res.json()["answer"].lower()
    spanish_keywords = ["compost", "materia", "orgánico", "orgánica", "capas", "humedad", "descomposición"]
    assert any(kw in answer for kw in spanish_keywords), (
        f"Expected Spanish answer. Got: {answer[:200]}"
    )


def test_chat_different_questions_return_different_answers(client, auth_headers):
    """Regression: routing returns contextually different answers."""
    res_a = client.post(
        "/chat",
        json={"question": "What pests attack pepper plants?"},
        headers=auth_headers,
    )
    res_b = client.post(
        "/chat",
        json={"question": "How do I make compost?"},
        headers=auth_headers,
    )
    assert res_a.status_code == 200
    assert res_b.status_code == 200
    assert res_a.json()["answer"] != res_b.json()["answer"]


def test_rate_limit_blocks_excess_requests(client):
    """After N requests, the N+1th returns 429 without hitting OpenAI."""
    # Register a dedicated user so this test is isolated from auth_headers fixtures
    client.post("/auth/register", json={"email": "ratelimit@growsage.com", "password": "testpass123"})
    res = client.post("/auth/login", json={"email": "ratelimit@growsage.com", "password": "testpass123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    os.environ["DAILY_REQUEST_LIMIT"] = "1"
    try:
        res1 = client.post("/chat", json={"question": "How do I grow tomatoes?"}, headers=headers)
        assert res1.status_code == 200, f"First request should succeed: {res1.json()}"

        res2 = client.post("/chat", json={"question": "How do I grow tomatoes?"}, headers=headers)
        assert res2.status_code == 429
        assert "Daily limit" in res2.json()["detail"]
    finally:
        del os.environ["DAILY_REQUEST_LIMIT"]


def test_rate_limit_is_per_user(client):
    """Exhausting one user's quota does not affect another user's independent counter."""
    for email in ("rl_a@growsage.com", "rl_b@growsage.com"):
        client.post("/auth/register", json={"email": email, "password": "testpass123"})

    def _headers(email: str) -> dict:
        res = client.post("/auth/login", json={"email": email, "password": "testpass123"})
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    headers_a = _headers("rl_a@growsage.com")
    headers_b = _headers("rl_b@growsage.com")

    os.environ["DAILY_REQUEST_LIMIT"] = "1"
    try:
        # Exhaust user A's quota (1st call succeeds, 2nd is blocked)
        client.post("/chat", json={"question": "How do I grow tomatoes?"}, headers=headers_a)
        blocked = client.post("/chat", json={"question": "test"}, headers=headers_a)
        assert blocked.status_code == 429

        # User B has an independent counter — first request still succeeds
        res_b = client.post("/chat", json={"question": "How do I grow tomatoes?"}, headers=headers_b)
        assert res_b.status_code == 200
    finally:
        del os.environ["DAILY_REQUEST_LIMIT"]
