FROM node:20-alpine AS web-builder
WORKDIR /webapp
COPY webapp/package.json webapp/package-lock.json ./
RUN npm ci
COPY webapp/ ./
RUN npm run build

FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04 AS api
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.local/bin:/opt/mtor-nexus/.venv/bin:${PATH}" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv python install 3.11
WORKDIR /opt/mtor-nexus
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY data ./data
RUN uv sync --frozen --no-dev
COPY --from=web-builder /webapp/.next ./webapp/.next
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "mtor_nexus.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
