"""Generate a machine-readable index of pinned source handling."""

import argparse
import json
from pathlib import Path
from typing import Any

from mtor_nexus.ingest.source_registry import load_source_registry, restricted_sources

SOURCE_HANDLING = {
    "uniprot": "resolved-accession-snapshot",
    "pdb": "resolved-structure-identifiers",
    "reactome": "pinned-root-pathway-overlay",
    "kegg": "pinned-pathway-overlay-metadata-only",
    "string": "configured-cross-validation-overlay",
    "biogrid": "configured-cross-validation-overlay",
    "phosphositeplus": "segregated-derived-site-identifiers-only",
    "clinvar": "open-germline-variant-references",
    "cbioportal": "derived-cohort-frequency-overlay",
    "cosmic": "segregated-licensed-local-reconciliation-overlay",
    "chembl": "rdkit-standardized-bioactivity-counter-screen-snapshot",
    "klifs": "aligned-pocket-descriptor-ingestion-pending",
}


def build_source_index(
    accession_path: str = "data/curated/uniprot-accessions.json",
) -> dict[str, Any]:
    """Describe committed source-derived artifacts and segregation boundaries."""

    registry = load_source_registry()
    accession_count = len(json.loads(Path(accession_path).read_text(encoding="utf-8")))
    return {
        "schema_version": "0.6.0",
        "sources": {
            name: {
                "version": source.version,
                "license": source.license,
                "url": source.url,
                "redistribution": source.redistribution,
                "handling": SOURCE_HANDLING[name],
                "options": source.options,
            }
            for name, source in registry.items()
        },
        "derived_artifacts": {
            "uniprot_accessions": {
                "path": accession_path,
                "record_count": accession_count,
                "fields": ["gene_symbol", "uniprot_accession"],
            },
            "normalized_graph": {
                "path": "data/processed/mtor-graph.json",
                "fields": ["nodes", "edges", "source_refs"],
            },
            "disease_layer": {
                "path": "data/processed/disease-layer.json",
                "fields": ["disease_classes", "associations", "mutations"],
            },
            "drug_layer": {
                "path": "data/processed/drug-layer.json",
                "fields": ["generations", "drugs", "target_links", "bioactivity"],
            },
            "ai_engine_status": {
                "path": "data/processed/ai-engine-status.json",
                "fields": ["scientific_release_ready", "selectivity_gnn", "architecture_contract"],
            },
        },
        "segregated_raw_sources": sorted(restricted_sources(registry)),
    }


def main() -> int:
    """Write the committed source index."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/sources/source-index.json")
    args = parser.parse_args()
    index = build_source_index()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"indexed {len(index['sources'])} pinned source(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
