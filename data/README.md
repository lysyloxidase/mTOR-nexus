# Data layout

`raw/` is reserved for immutable, DVC-managed source snapshots. `processed/`
contains normalized FAIR graph exports. Every downloaded snapshot must append a
record to `provenance.jsonl` with source, version, SHA-256 digest, and UTC
timestamp before it enters an ingestion workflow.

The Phase 2 normalized graph is `processed/mtor-graph.json`. GraphML, JSON-LD,
Parquet, and per-module Cytoscape exports are regenerated with `make data`.
`processed/export-manifest.json` records SHA-256 digests for each exchange
artifact.

`sources/source-index.json` records pinned source handling. Raw
PhosphoSitePlus snapshots remain under `sources/restricted/` locally and are
never committed because their license is non-commercial.
