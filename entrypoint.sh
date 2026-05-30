#!/bin/sh
# Auto-ingest PDFs on first boot if the vectorstore is empty.
PERSIST_DIR="${CHROMA_PERSIST_DIR:-vectorstore}"

if [ ! -f "$PERSIST_DIR/chroma.sqlite3" ]; then
    echo "[entrypoint] Vectorstore not found — running ingestion (this may take a few minutes)..."
    python ingest.py
    echo "[entrypoint] Ingestion complete."
else
    echo "[entrypoint] Vectorstore already populated — skipping ingestion."
fi

exec uvicorn api:app --host 0.0.0.0 --port "${PORT:-8000}"
