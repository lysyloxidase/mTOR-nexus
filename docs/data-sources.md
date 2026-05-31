# Data Sources

Pinned source configuration lives in `src/mtor_nexus/config/data_sources.yaml`.

| Source | Purpose | Validation |
| --- | --- | --- |
| UniProt | Protein accessions | Weekly REST resolution |
| RCSB PDB | Structural identifiers | Weekly REST resolution |
| Crossref | Bibliography DOIs | Weekly REST resolution |
| PhosphoSitePlus | Phosphorylation-site identifiers | Manual licensed ingestion |

Phase 2 ingestion must record every downloaded snapshot in
`data/provenance.jsonl` before normalization.
