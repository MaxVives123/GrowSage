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


def create_app(db_url: str | None = None) -> FastAPI:
    engine = make_engine(db_url)
    Base.metadata.create_all(engine)

    app = FastAPI(title="GrowSage API", version="2.0.0")

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
        return {"status": "ok", "version": "2.0.0"}

    return app


# Module-level instance for uvicorn
app = create_app()
