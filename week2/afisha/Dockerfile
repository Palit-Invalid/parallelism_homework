ARG WORKDIR=/app

FROM astral/uv:python3.13-trixie-slim AS builder

ARG WORKDIR
WORKDIR "$WORKDIR"

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_LOCKED=1
ENV UV_NO_INSTALL_PROJECT=1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync


FROM python:3.13-slim-trixie

ARG WORKDIR
WORKDIR "$WORKDIR"

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

ARG UID=1000
ARG GID=1000
ARG USERNAME=app

# Setup a non-root user
RUN groupadd --system --gid $GID $USERNAME \
    && useradd --system --gid $GID --uid $UID --create-home $USERNAME

COPY --from=builder --chown=$USERNAME:$USERNAME $WORKDIR $WORKDIR
ENV PATH="$WORKDIR/.venv/bin:$PATH"

COPY src src
COPY migrations migrations
COPY alembic.ini .

ENV GRANIAN_HOST=0.0.0.0
ENV GRANIAN_PORT=8000
ENV GRANIAN_INTERFACE=asgi
ENV GRANIAN_LOOP=uvloop
ENV GRANIAN_RELOAD=false
ENV GRANIAN_WORKERS=1

ENV PATH="$WORKDIR/.venv/bin:$PATH"

USER $USERNAME

ENTRYPOINT ["granian", "src.main:app"]
