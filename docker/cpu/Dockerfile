FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim AS builder

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    libshout3-dev

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.10-slim-bookworm AS prod

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    libgomp1 \
    libshout3-dev

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["wet-toast"]