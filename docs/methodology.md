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

Raw source snapshots are immutable and DVC-managed where redistribution rights
allow it. Each snapshot appends a source, pinned version, SHA-256 digest, and
UTC timestamp to `data/provenance.jsonl`. Normalized JSON-LD, GraphML, Parquet,
and per-module Cytoscape exports are committed for exchange.

PhosphoSitePlus raw exports are a deliberate exception: licensed snapshots stay
segregated and uncommitted. Only derived site identifiers and phospho-site
labels enter the open normalized graph.

## FAIR principles

The project includes machine-readable citation metadata, CodeMeta metadata,
Zenodo deposit metadata, stable biological identifiers, explicit licensing,
and scheduled identifier-resolution checks.

## AI prerelease policy

The Phase 6 serving surface is fail-closed. RDKit standardization runs before
Morgan radius-2 fingerprint comparison against committed ChEMBL-derived
structures. Queries with nearest-neighbor Tanimoto below `0.3` are refused as
out of domain. In-domain queries are also refused until the registered
five-target architecture passes its locked metrics, Torin2 benchmark,
deterministic-weight check, and single-A100 no-OOM run.
