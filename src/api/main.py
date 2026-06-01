"""FastAPI application factory."""
from __future__ import annotations
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import auth, chat, conversations
from src.infrastructure.database import make_engine, Base

load_dotenv()


def _cors_origins() -> list[str]:
    """Read allowed origins from env — comma-separated for multi-domain."""
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]


def _is_dev() -> bool:
    return os.getenv("ENVIRONMENT", "production").lower() == "development"


def create_app(db_url: str | None = None) -> FastAPI:
    engine = make_engine(db_url)
    Base.metadata.create_all(engine)

    # Disable interactive docs in production — /docs and /redoc are public by default
    app = FastAPI(
        title="GrowSage API",
        version="2.0.0",
        docs_url="/docs" if _is_dev() else None,
        redoc_url="/redoc" if _is_dev() else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(chat.router)
    app.include_router(conversations.router)

    @app.get("/health", tags=["meta"])
    def health():
        import redis as redis_lib
        redis_url = os.getenv("REDIS_URL", "")
        redis_status = "no url"
        cache_keys = 0
        if redis_url:
            try:
                r = redis_lib.from_url(redis_url, decode_responses=True, socket_connect_timeout=3)
                r.ping()
                cache_keys = len(r.keys("chat:*"))
                redis_status = "ok"
            except Exception as e:
                redis_status = f"error: {type(e).__name__}: {str(e)[:120]}"
        return {
            "status": "ok",
            "version": "2.0.0",
            "redis": redis_status,
            "cache_keys": cache_keys,
            "redis_url_prefix": redis_url[:25] if redis_url else None,
        }

    return app


# Module-level instance for uvicorn
app = create_app()
