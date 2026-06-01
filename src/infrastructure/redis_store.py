"""Redis adapter — IP rate limiting and response caching.

Designed to degrade gracefully: if Redis is unavailable every function
returns a safe default so the app keeps working without it.
"""
from __future__ import annotations
import hashlib
import json
import os

_pool = None


def _client():
    """Return a Redis client from the shared pool, or None if unavailable."""
    global _pool
    try:
        import redis
        if _pool is None:
            url = os.getenv("REDIS_URL", "redis://localhost:6379")
            _pool = redis.ConnectionPool.from_url(url, decode_responses=True)
        return redis.Redis(connection_pool=_pool)
    except Exception:
        return None


# ── IP rate limiting ──────────────────────────────────────────────────────────

def check_ip_limit(
    ip: str,
    max_attempts: int = 5,
    window_seconds: int = 3600,
) -> bool:
    """Return True if the IP is within the allowed limit, False if blocked.

    Falls back to True (allow) when Redis is unreachable so the app keeps
    working in local development without a Redis instance.
    """
    r = _client()
    if r is None:
        return True  # graceful fallback
    try:
        key = f"register:ip:{ip}"
        count = r.incr(key)
        if count == 1:
            r.expire(key, window_seconds)
        return int(count) <= max_attempts
    except Exception:
        return True  # graceful fallback


# ── Response cache ────────────────────────────────────────────────────────────

_CACHE_TTL = 60 * 60 * 24  # 24 hours
_CACHE_VERSION = "v1"


def _cache_key(question: str) -> str:
    normalized = question.strip().lower()
    digest = hashlib.md5(normalized.encode()).hexdigest()
    return f"chat:{_CACHE_VERSION}:{digest}"


def get_cached_response(question: str) -> dict | None:
    """Return {"answer": str, "sources": list} if cached, else None."""
    r = _client()
    if r is None:
        return None
    try:
        raw = r.get(_cache_key(question))
        return json.loads(raw) if raw else None
    except Exception:
        return None


def cache_response(question: str, answer: str, sources: list) -> None:
    """Store the answer and sources for a question for 24 hours."""
    r = _client()
    if r is None:
        return
    try:
        r.setex(
            _cache_key(question),
            _CACHE_TTL,
            json.dumps({"answer": answer, "sources": sources}),
        )
    except Exception:
        pass  # cache failures are non-fatal
