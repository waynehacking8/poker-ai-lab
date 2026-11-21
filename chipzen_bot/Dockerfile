# syntax=docker/dockerfile:1.7
#
# Chipzen image for the poker-ai-lab Hold'em bot, adapted from the SDK's Python starter.
# Pure Python (no compiled extensions), so the image stays small and seccomp-safe.
# The strategy source is shipped as plain .py files (Cython IP protection is optional
# and not used here).
#
# Build:   docker build -t holdem-bot:test .
# Export:  docker save holdem-bot:test | gzip > holdem-bot.tar.gz
#
# Base pinned by digest, same as the SDK starter (tag python:3.12-slim).
FROM python:3.12-slim@sha256:dd29372629eeba2dd003fd9e9d35a5b8236c44727875a0364254b5127af88e65

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /bot

COPY requirements.txt .
RUN pip install -r requirements.txt \
    && find /usr/local/lib/python3.12 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.12 -type d -name tests -exec rm -rf {} + 2>/dev/null || true

# Entry point plus the strategy package (code and the two small data tables).
COPY bot.py /bot/bot.py
COPY nlhe/ /bot/nlhe/

# Run as non-root; the platform adds seccomp and cap-drop on top.
RUN groupadd --system --gid 10001 bot && \
    useradd --system --uid 10001 --gid bot --home-dir /bot --shell /usr/sbin/nologin bot && \
    chown -R bot:bot /bot
USER 10001

ENTRYPOINT ["python", "-c", "from bot import main; main()"]
