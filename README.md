# mTOR-NEXUS

**A provenance-first interactive atlas of mTOR signaling and a foundation for
AI-assisted drug discovery.**

mTOR-NEXUS models proteins, complexes, metabolites, and small molecules as a
heterogeneous graph. Every interaction carries a pre-registered evidence tier,
one or more species-provenance flags, and primary citations. The first phase
ships the schema, curated seed graph, governance metadata, validation tools,
container frame, and CI policy.

## Why this atlas is strict

Mechanistic confidence and translational relevance are separate questions.
Human, rodent, structural, biochemical, and computational claims are therefore
recorded explicitly rather than blended into a single confidence label. See
the [tier and species rubric](docs/tier-species-rubric.md) and the
[nomenclature guards](docs/nomenclature-guards.md).

## Quick start

```bash
uv sync --all-extras
uv run pytest
docker compose up --build
```

The API serves `GET /health` and `GET /graph` on port `8000`. The Phase 1
webapp is exposed on port `3000`, with Neo4j on ports `7474` and `7687`.

## Provenance and FAIR governance

- Code is Apache-2.0 licensed.
- Figures and data are CC-BY-4.0 licensed.
- Downloaded source snapshots are recorded in `data/provenance.jsonl`.
- Citation metadata lives in `CITATION.cff`, `codemeta.json`, and `zenodo.json`.
- Weekly CI resolves bibliography DOIs, UniProt accessions, and PDB IDs.

## AI model cards

No predictive model ships in Phase 1. Each future model must receive a model
card before it can be surfaced by the application. The required template is
documented in [AI model cards](docs/ai-model-cards.md).

## Research-use notice

mTOR-NEXUS is research software. It is not validated for clinical use and must
not be used to make treatment decisions.
