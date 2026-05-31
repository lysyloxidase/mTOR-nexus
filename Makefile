.PHONY: all quality test docs data graph graph-validate source-probe web web-lint web-build train figs

all: quality test docs graph-validate

quality:
	uv run ruff check .
	uv run ruff format --check .
	uv run pyright

test:
	uv run pytest

docs:
	uv run mkdocs build --strict

data:
	uv run python -m mtor_nexus.ingest.source_index
	uv run python -m mtor_nexus.graph.build

graph:
	uv run python -m mtor_nexus.graph.build

graph-validate:
	uv run python -m mtor_nexus.graph.validate

source-probe:
	uv run python -m mtor_nexus.ingest.live_probe

web:
	docker run --rm -v "$(CURDIR)/webapp:/app" -w /app node:20-alpine npm run dev

web-lint:
	docker run --rm -v "$(CURDIR)/webapp:/app" -w /app node:20-alpine npm run lint

web-build:
	docker run --rm -v "$(CURDIR)/webapp:/app" -w /app node:20-alpine npm run build

train:
	@echo "Phase 6 model training is not implemented yet."

figs:
	@echo "Reproducible figure notebooks will arrive with curated Phase 2 data."
