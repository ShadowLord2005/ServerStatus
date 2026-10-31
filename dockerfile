FROM ghcr.io/astral-sh/uv:python3.14-alpine


WORKDIR /app

ENV UV_NO_DEV=1
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_CACHE_DIR=/root/.cache/uv/python
ENV UV_CACHE_DIR=/opt/uv-cache/
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock /app/ 

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY --exclude=docker* . /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked  

CMD [ "uv", "run", "serverstatus" ]