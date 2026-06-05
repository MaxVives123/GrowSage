"""FastAPI application factory."""
from __future__ import annotations
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import auth, chat, conversations
from src.infrastructure.database import make_engine, Base

load_dotenv()


def _init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN", "")
    if not dsn:
        return
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("ENVIRONMENT", "production"),
        traces_sample_rate=0.2,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        send_default_pii=False,
    )


def _cors_origins() -> list[str]:
    """Read allowed origins from env — comma-separated for multi-domain."""
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]


def _is_dev() -> bool:
    return os.getenv("ENVIRONMENT", "production").lower() == "development"


def create_app(db_url: str | None = None) -> FastAPI:
    _init_sentry()
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
        return {"status": "ok", "version": "2.0.0"}

    return app


# Module-level instance for uvicorn
app = create_app()
