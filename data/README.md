# Data layout

`raw/` is reserved for immutable, DVC-managed source snapshots. `processed/`
contains normalized FAIR graph exports. Every downloaded snapshot must append a
record to `provenance.jsonl` with source, version, SHA-256 digest, and UTC
timestamp before it enters an ingestion workflow.

The Phase 1 seed graph is `processed/mtor-graph.json`. Phase 2 will add Parquet
exports while retaining JSON-LD for portable exchange.
