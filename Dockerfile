FROM python:3.13.11-slim

# Copy uv binary from official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

# Add virtual environment to PATH so we can use installed packages
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files
COPY "pyproject.toml" "uv.lock" ".python-version" ./

# Install dependencies
RUN uv sync --locked

COPY ingestion_pipeline.py.py pipeline.py

ENTRYPOINT ["python", "pipeline.py"]
