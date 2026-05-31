.PHONY: all quality test docs data graph train figs

all: quality test docs graph

quality:
	uv run ruff check .
	uv run ruff format --check .
	uv run pyright

test:
	uv run pytest

docs:
	uv run mkdocs build --strict

data:
	@echo "Phase 2 ingestion loaders are not implemented yet."

graph:
	uv run python -m mtor_nexus.utils.tier_species_validation

train:
	@echo "Phase 6 model training is not implemented yet."

figs:
	@echo "Reproducible figure notebooks will arrive with curated Phase 2 data."
