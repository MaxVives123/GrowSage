FROM python:3.12-slim

WORKDIR /app

# System deps needed by chromadb and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    langchain==0.3.25 \
    langchain-openai==0.3.19 \
    langchain-community==0.3.24 \
    langchain-chroma==0.2.4 \
    "chromadb>=1.0.9" \
    openai==1.82.1 \
    python-dotenv==1.1.0 \
    pypdf==5.5.0 \
    beautifulsoup4==4.13.4 \
    requests==2.32.3 \
    tiktoken==0.9.0 \
    rich==14.0.0 \
    fastapi==0.115.12 \
    "uvicorn[standard]==0.34.3" \
    sqlalchemy==2.0.50 \
    "passlib[bcrypt]==1.7.4" \
    "bcrypt==4.0.1" \
    "python-jose[cryptography]==3.3.0" \
    psycopg2-binary

COPY . .

EXPOSE 8000

CMD sh -c "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"
