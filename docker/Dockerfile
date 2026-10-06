FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libmagic-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Force uv to use a specific venv path and Python version
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_PYTHON_PREFERENCE=only-system
RUN uv sync --frozen --no-dev

# Copy app code
COPY . .

# Run via the venv directly (NOT uv run)
CMD ["sh", "-c", "/app/.venv/bin/uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]