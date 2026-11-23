# syntax=docker/dockerfile:1.7
#
# Chipzen image for the RL Distill1Bot. Build context is the repo root (see deploy/README.md).
# Ships only what the bot imports at runtime: rl/{bot,bot_distill,features,runtime}.py, the
# chosen weights and nlhe/{cards,evaluator,preflop} with its data. No torch, numba, training
# code, specialists or teacher.
#
# Base pinned by digest, same as chipzen_bot/Dockerfile (tag python:3.12-slim).
FROM python:3.12-slim@sha256:dd29372629eeba2dd003fd9e9d35a5b8236c44727875a0364254b5127af88e65

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /bot

COPY deploy/requirements.txt .
RUN pip install -r requirements.txt \
    && find /usr/local/lib/python3.12 -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.12 -type d -name tests -exec rm -rf {} + 2>/dev/null || true

COPY deploy/bot.py /bot/bot.py
COPY rl/__init__.py rl/allin.py rl/bot.py rl/bot_distill.py rl/features.py rl/runtime.py /bot/rl/
# Match-value tables for answering a near-certain shover (rl/allin.py, tools/allin_tables.py).
COPY rl/models/allin_v.npz /bot/rl/models/allin_v.npz
# Per-opponent-name starting counts for the in-match tracker (rl/features.py load_priors, tools/tracker_profiles.py).
COPY rl/models/tracker_prior.npz /bot/rl/models/tracker_prior.npz
# Weights: any repo path via --build-arg MODEL=..., installed under a fixed name.
ARG MODEL=rl/models/distill1.npz
COPY ${MODEL} /bot/rl/models/weights.npz
COPY chipzen_bot/nlhe/__init__.py chipzen_bot/nlhe/cards.py chipzen_bot/nlhe/evaluator.py chipzen_bot/nlhe/preflop.py /bot/nlhe/
COPY chipzen_bot/nlhe/data/ /bot/nlhe/data/

# Run as non-root; the platform adds seccomp and cap-drop on top.
RUN groupadd --system --gid 10001 bot && \
    useradd --system --uid 10001 --gid bot --home-dir /bot --shell /usr/sbin/nologin bot && \
    chown -R bot:bot /bot
USER 10001

ENTRYPOINT ["python", "-c", "from bot import main; main()"]
