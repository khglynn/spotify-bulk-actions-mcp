FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
RUN groupadd -r app && useradd -r -g app -d /app app

# Dependency layer first for build caching
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY spotify_bulk_actions_mcp ./spotify_bulk_actions_mcp
RUN uv sync --frozen --no-dev && chown -R app:app /app

ENV MCP_TRANSPORT=http \
    PATH="/app/.venv/bin:$PATH"

USER app
EXPOSE 8080
CMD ["spotify-bulk-actions-mcp"]
