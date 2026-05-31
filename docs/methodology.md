# Methodology

## Curation model

The graph separates entities from mechanistic claims. Nodes represent proteins,
complexes, metabolites, lipids, receptors, sensors, and small molecules. Edges
represent typed interactions such as phosphorylation, recruitment, inhibition,
or binding.

Each edge requires:

- a pre-registered evidence tier;
- one or more species or experimental-context flags;
- at least one primary citation;
- a phospho-site and PhosphoSitePlus identifier for phosphorylation edges.

## Provenance

Raw source snapshots will be immutable and DVC-managed beginning in Phase 2.
Each snapshot appends a source, pinned version, SHA-256 digest, and UTC timestamp
to `data/provenance.jsonl`. Normalized JSON-LD is committed for exchange;
Parquet exports will be generated as ingestion volume increases.

## FAIR principles

The project includes machine-readable citation metadata, CodeMeta metadata,
Zenodo deposit metadata, stable biological identifiers, explicit licensing,
and scheduled identifier-resolution checks.
