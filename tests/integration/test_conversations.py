"""
Integration tests — Streaming, conversations, and feedback.
No mocks: real ChromaDB + real OpenAI + real SQLite.
"""
import json


# ── helpers ───────────────────────────────────────────────────────────────────

def _sse(text: str) -> list[dict]:
    """Parse SSE response body into a list of event dicts."""
    events = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("data: "):
            try:
                events.append(json.loads(line[6:]))
            except json.JSONDecodeError:
                pass
    return events


def _stream(client, headers, question, history=None, conversation_id=None):
    payload = {"question": question, "history": history or []}
    if conversation_id:
        payload["conversation_id"] = conversation_id
    res = client.post("/chat/stream", json=payload, headers=headers)
    return res, _sse(res.text)


# ── streaming ─────────────────────────────────────────────────────────────────

def test_stream_requires_auth(client):
    res = client.post("/chat/stream", json={"question": "test"})
    assert res.status_code == 403


def test_stream_rejects_empty_question(client, auth_headers):
    res = client.post("/chat/stream", json={"question": "   "}, headers=auth_headers)
    assert res.status_code == 422


def test_stream_returns_valid_sse_events(client, auth_headers):
    """Full flow: sources → tokens → done, all with correct structure."""
    res, events = _stream(client, auth_headers, "How do I grow tomatoes?")

    assert res.status_code == 200
    assert "text/event-stream" in res.headers.get("content-type", "")

    types = [e["type"] for e in events]
    assert "sources" in types
    assert "token" in types
    assert "done" in types

    src_evt = next(e for e in events if e["type"] == "sources")
    assert "conversation_id" in src_evt
    assert len(src_evt["sources"]) >= 1

    all_tokens = "".join(e["content"] for e in events if e["type"] == "token")
    assert len(all_tokens) > 20, "Expected a meaningful streamed answer"


def test_stream_creates_conversation_and_persists_messages(client, auth_headers):
    """Streaming auto-creates a conversation and saves user + assistant messages."""
    before = len(client.get("/conversations", headers=auth_headers).json())

    res, events = _stream(client, auth_headers, "What pests attack pepper plants?")
    assert res.status_code == 200

    src_evt = next(e for e in events if e["type"] == "sources")
    done_evt = next(e for e in events if e["type"] == "done")
    conv_id = src_evt["conversation_id"]
    msg_id = done_evt["message_id"]

    # Conversation was created
    after = client.get("/conversations", headers=auth_headers).json()
    assert len(after) == before + 1

    # Both messages persisted
    msgs = client.get(f"/conversations/{conv_id}/messages", headers=auth_headers).json()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["id"] == msg_id
    assert len(msgs[1]["sources"]) >= 1


def test_stream_continues_existing_conversation(client, auth_headers):
    """Using conversation_id keeps all messages in the same thread."""
    _, events1 = _stream(client, auth_headers, "How do I grow tomatoes?")
    conv_id = next(e for e in events1 if e["type"] == "sources")["conversation_id"]

    _, events2 = _stream(
        client, auth_headers,
        question="What about watering them?",
        history=[
            {"role": "user", "content": "How do I grow tomatoes?"},
            {"role": "assistant", "content": "Plant them in well-drained soil."},
        ],
        conversation_id=conv_id,
    )
    conv_id_2 = next(e for e in events2 if e["type"] == "sources")["conversation_id"]

    assert conv_id == conv_id_2

    msgs = client.get(f"/conversations/{conv_id}/messages", headers=auth_headers).json()
    assert len(msgs) == 4  # 2 turns × (user + assistant)


def test_stream_rate_limit_blocks_excess(client):
    """Rate limit also applies to the streaming endpoint."""
    client.post("/auth/register", json={"email": "rl_stream@growsage.com", "password": "testpass123"})
    token = client.post(
        "/auth/login", json={"email": "rl_stream@growsage.com", "password": "testpass123"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    import os
    os.environ["DAILY_REQUEST_LIMIT"] = "1"
    try:
        r1 = client.post("/chat/stream", json={"question": "test"}, headers=headers)
        assert r1.status_code == 200
        r2 = client.post("/chat/stream", json={"question": "test"}, headers=headers)
        assert r2.status_code == 429
    finally:
        del os.environ["DAILY_REQUEST_LIMIT"]


# ── conversation CRUD ─────────────────────────────────────────────────────────

def test_list_conversations_requires_auth(client):
    assert client.get("/conversations").status_code == 403


def test_list_conversations_returns_list(client, auth_headers):
    res = client.get("/conversations", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_get_messages_requires_auth(client):
    assert client.get("/conversations/fake/messages").status_code == 403


def test_get_messages_404_for_unknown(client, auth_headers):
    res = client.get("/conversations/does-not-exist/messages", headers=auth_headers)
    assert res.status_code == 404


def test_conversations_isolated_between_users(client):
    """Conversations created by one user are invisible to another."""
    client.post("/auth/register", json={"email": "user_a@growsage.com", "password": "testpass123"})
    client.post("/auth/register", json={"email": "user_b@growsage.com", "password": "testpass123"})
    tok_a = client.post("/auth/login", json={"email": "user_a@growsage.com", "password": "testpass123"}).json()["access_token"]
    tok_b = client.post("/auth/login", json={"email": "user_b@growsage.com", "password": "testpass123"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {tok_a}"}
    headers_b = {"Authorization": f"Bearer {tok_b}"}

    # User A creates a conversation
    _, events = _stream(client, headers_a, "How do I grow tomatoes?")
    conv_id_a = next(e for e in events if e["type"] == "sources")["conversation_id"]

    # User B cannot access user A's conversation
    res = client.get(f"/conversations/{conv_id_a}/messages", headers=headers_b)
    assert res.status_code == 404


def test_delete_conversation(client, auth_headers):
    """Deleting removes the conversation and its messages."""
    _, events = _stream(client, auth_headers, "How do I make compost?")
    conv_id = next(e for e in events if e["type"] == "sources")["conversation_id"]

    assert client.delete(f"/conversations/{conv_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/conversations/{conv_id}/messages", headers=auth_headers).status_code == 404


# ── feedback ──────────────────────────────────────────────────────────────────

def test_submit_positive_feedback(client, auth_headers):
    _, events = _stream(client, auth_headers, "How do I grow tomatoes?")
    msg_id = next(e for e in events if e["type"] == "done")["message_id"]

    res = client.post(
        f"/conversations/messages/{msg_id}/feedback",
        json={"rating": 1},
        headers=auth_headers,
    )
    assert res.status_code == 204


def test_submit_negative_feedback(client, auth_headers):
    _, events = _stream(client, auth_headers, "How do I make compost?")
    msg_id = next(e for e in events if e["type"] == "done")["message_id"]

    res = client.post(
        f"/conversations/messages/{msg_id}/feedback",
        json={"rating": -1},
        headers=auth_headers,
    )
    assert res.status_code == 204


def test_feedback_invalid_rating_returns_422(client, auth_headers):
    res = client.post(
        "/conversations/messages/any-id/feedback",
        json={"rating": 5},
        headers=auth_headers,
    )
    assert res.status_code == 422


def test_feedback_requires_auth(client):
    assert client.post("/conversations/messages/any/feedback", json={"rating": 1}).status_code == 403
