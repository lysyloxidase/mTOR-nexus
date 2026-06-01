# Data Sources

Pinned source configuration lives in `src/mtor_nexus/config/data_sources.yaml`.
The machine-readable handling index is `data/sources/source-index.json`.

| Source | Pin | Handling |
| --- | --- | --- |
| UniProt | `2025_03` | Committed derived human accession snapshot |
| RCSB PDB | `2025-05-snapshot` | Resolved structural identifiers on nodes |
| Reactome | `v90`, `R-HSA-165159` | Root-pathway reconciliation overlay |
| KEGG | `2025-05`, `hsa04150` | Metadata-only pathway overlay |
| STRING | `12.0`, score `>=700` | Configured PPI cross-validation overlay |
| BioGRID | `4.4.X` | Configured PPI cross-validation overlay |
| PhosphoSitePlus | `2025-snapshot` | Segregated raw snapshot; derived site IDs only |
| ClinVar | `2026-06-live-eutils` | Open germline variant references |
| cBioPortal | `2026-06-public-api` | Derived cohort frequencies and API references |
| COSMIC | `licensed-local-snapshot` | Segregated local reconciliation overlay only |

## Refresh boundaries

`uv run python -m mtor_nexus.ingest.uniprot_refresh` refreshes the committed
derived UniProt map. `make source-probe` checks open KEGG, Reactome, and STRING
endpoints without writing upstream records. `make data` regenerates normalized
artifacts deterministically from the committed catalog and accession snapshot.

`make disease-probe` calculates the current TCGA Firehose Legacy ER-positive
breast PIK3CA mutation-only frequency through cBioPortal and verifies the MTOR
`p.Glu1799Lys` ClinVar search surface. Raw COSMIC rows are never committed.

The public live endpoints can move independently of the pins. A live probe is
an availability check, not permission to mutate a release artifact.
