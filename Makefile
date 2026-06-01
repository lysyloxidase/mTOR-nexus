.PHONY: all quality test docs data graph graph-validate disease-validate drug-validate ai-validate drug-refresh source-probe disease-probe web web-lint web-build train figs

all: quality test docs graph-validate disease-validate drug-validate ai-validate

quality:
	uv run ruff check .
	uv run ruff format --check .
	uv run pyright

test:
	uv run pytest

docs:
	uv run mkdocs build --strict

data:
	uv run python -m mtor_nexus.ai.validate
	uv run python -m mtor_nexus.ingest.source_index
	uv run python -m mtor_nexus.graph.build

graph:
	uv run python -m mtor_nexus.graph.build

graph-validate:
	uv run python -m mtor_nexus.graph.validate

disease-validate:
	uv run python -m mtor_nexus.disease.validate

drug-validate:
	uv run python -m mtor_nexus.drugs.validate

ai-validate:
	uv run python -m mtor_nexus.ai.validate

drug-refresh:
	uv run python -m mtor_nexus.drugs.bioactivity

source-probe:
	uv run python -m mtor_nexus.ingest.live_probe

disease-probe:
	uv run python -m mtor_nexus.disease.live_probe

web:
	docker run --rm -v "$(CURDIR)/webapp:/app" -w /app node:20-alpine npm run dev

web-lint:
	docker run --rm -v "$(CURDIR)/webapp:/app" -w /app node:20-alpine npm run lint

web-build:
	docker run --rm -v "$(CURDIR)/webapp:/app" -w /app node:20-alpine npm run build

train:
	@echo "Blocked: ingest adequate five-target ChEMBL + KLIFS data before training the locked Phase 6 architecture."

figs:
	@echo "Reproducible figure notebooks will arrive with curated Phase 2 data."
