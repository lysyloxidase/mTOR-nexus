# Data Sources

Pinned source configuration lives in `src/mtor_nexus/config/data_sources.yaml`.
The machine-readable handling index is `data/sources/source-index.json`.

| Source | Pin | Phase 2 handling |
| --- | --- | --- |
| UniProt | `2025_03` | Committed derived human accession snapshot |
| RCSB PDB | `2025-05-snapshot` | Resolved structural identifiers on nodes |
| Reactome | `v90`, `R-HSA-165159` | Root-pathway reconciliation overlay |
| KEGG | `2025-05`, `hsa04150` | Metadata-only pathway overlay |
| STRING | `12.0`, score `>=700` | Configured PPI cross-validation overlay |
| BioGRID | `4.4.X` | Configured PPI cross-validation overlay |
| PhosphoSitePlus | `2025-snapshot` | Segregated raw snapshot; derived site IDs only |

## Refresh boundaries

`uv run python -m mtor_nexus.ingest.uniprot_refresh` refreshes the committed
derived UniProt map. `make source-probe` checks open KEGG, Reactome, and STRING
endpoints without writing upstream records. `make data` regenerates normalized
artifacts deterministically from the committed catalog and accession snapshot.

The public live endpoints can move independently of the pins. A live probe is
an availability check, not permission to mutate a release artifact.
