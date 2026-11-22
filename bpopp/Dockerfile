# Isolated runtime for the third-party poker-solver blueprint (policy lookup only).
# Build context: the pinned poker-solver checkout. Our server comes in as the
# named context "ours".
FROM python:3.13-slim-bookworm AS build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/* && pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
ENV UV_PROJECT_ENVIRONMENT=/opt/venv UV_COMPILE_BYTECODE=1
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.13-slim-bookworm
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin bp
COPY --from=build /opt/venv /opt/venv
COPY src /app/src
COPY config /app/config
COPY --from=ours server.py /srv/server.py
ENV PATH=/opt/venv/bin:$PATH PYTHONPATH=/app PYTHONUNBUFFERED=1 \
    NUMBA_CACHE_DIR=/tmp/numba PYTHONDONTWRITEBYTECODE=1
USER 10001
WORKDIR /work
ENTRYPOINT ["python", "/srv/server.py"]
