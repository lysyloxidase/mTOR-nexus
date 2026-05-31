# Contributing to mTOR-NEXUS

Thanks for helping build a careful, provenance-first atlas.

## Development setup

1. Install Python 3.11 and [uv](https://docs.astral.sh/uv/).
2. Run `uv sync --all-extras`.
3. Run `uv run pre-commit install`.
4. Use `make all` before opening a pull request.

## Evidence requirements

Every new edge must include a tier, one or more species-evidence flags, and at
least one primary citation. Protein nodes require UniProt accessions.
Phosphorylation edges require a phospho-site and a resolvable PhosphoSitePlus
identifier. Use the issue templates for additions or citation corrections.

## Licensing

Code contributions are accepted under Apache-2.0. Figures and data
contributions are accepted under CC-BY-4.0.
