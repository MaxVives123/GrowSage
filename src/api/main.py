"""FastAPI application factory."""
from __future__ import annotations
import logging
import os
from dotenv import load_dotenv

# Structured security logger — one line per security event, easy to grep/ship to SIEM
security_log = logging.getLogger("growsage.security")
logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        expose_headers=["X-Request-ID"],
    )

    _MAX_BODY_BYTES = 64 * 1024  # 64 KB — generous for chat, blocks payload attacks

    @app.middleware("http")
    async def limit_body_size(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > _MAX_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"},
            )
        return await call_next(request)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Only send HSTS in production (Railway handles TLS termination)
        if not _is_dev():
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    app.include_router(auth.router)
    app.include_router(chat.router)
    app.include_router(conversations.router)

    @app.get("/health", tags=["meta"])
    def health():
        return {"status": "ok", "version": "2.0.0"}

    return app


# Module-level instance for uvicorn
app = create_app()
