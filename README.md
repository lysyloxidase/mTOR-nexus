# mTOR-NEXUS

**A provenance-first interactive atlas of mTOR signaling and a foundation for
AI-assisted drug discovery.**

mTOR-NEXUS models proteins, complexes, metabolites, and small molecules as a
heterogeneous graph. Every interaction carries a pre-registered evidence tier,
one or more species-provenance flags, and primary citations. Phase 2 ships a
curated pathway graph with 261 nodes and 234 evidence-tagged interactions,
deterministic exchange formats, and a Neo4j loader. Phase 3 adds a React Three
Fiber global explorer and seven synchronized Cytoscape.js SBGN-PD diagrams.

## Why this atlas is strict

Mechanistic confidence and translational relevance are separate questions.
Human, rodent, structural, biochemical, and computational claims are therefore
recorded explicitly rather than blended into a single confidence label. See
the [tier and species rubric](docs/tier-species-rubric.md) and the
[nomenclature guards](docs/nomenclature-guards.md).

## Quick start

```bash
uv sync --all-extras
make data
uv run pytest
docker compose up --build
```

The API serves `GET /health` and `GET /graph` on port `8000`. The Phase 3
webapp is exposed on port `3000`, with Neo4j on ports `7474` and `7687`.

## Provenance and FAIR governance

- Code is Apache-2.0 licensed.
- Figures and data are CC-BY-4.0 licensed.
- Downloaded source snapshots are recorded in `data/provenance.jsonl`.
- Pinned source policy lives in `src/mtor_nexus/config/data_sources.yaml`.
- Licensed PhosphoSitePlus raw exports remain segregated and uncommitted.
- Citation metadata lives in `CITATION.cff`, `codemeta.json`, and `zenodo.json`.
- Weekly CI resolves bibliography DOIs, UniProt accessions, and PDB IDs.

## AI model cards

No predictive model ships in Phase 2. Each future model must receive a model
card before it can be surfaced by the application. The required template is
documented in [AI model cards](docs/ai-model-cards.md).

## Research-use notice

mTOR-NEXUS is research software. It is not validated for clinical use and must
not be used to make treatment decisions.
