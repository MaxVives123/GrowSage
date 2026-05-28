# Backward-compat shim — real app lives in src/api/main.py
# Usage: uvicorn api:app --reload --port 8000
from src.api.main import app  # noqa: F401
