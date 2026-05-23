FROM python:3.13.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --extra local

COPY src/__init__.py src/fetch_data.py src/transform_data.py src/write_to_postgresql.py src/
COPY pipelines/__init__.py pipelines/local_pipeline.py pipelines/

ENTRYPOINT ["python", "-m", "pipelines.local_pipeline"]
