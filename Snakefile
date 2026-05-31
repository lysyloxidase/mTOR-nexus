"""Phase 2 normalized graph export DAG."""

rule all:
    input:
        "data/processed/export-manifest.json"


rule source_index:
    input:
        "data/curated/uniprot-accessions.json",
        "src/mtor_nexus/config/data_sources.yaml",
    output:
        "data/sources/source-index.json",
    shell:
        "uv run python -m mtor_nexus.ingest.source_index"


rule graph_exports:
    input:
        "data/sources/source-index.json",
        "src/mtor_nexus/graph/catalog.py",
        "src/mtor_nexus/graph/curated_edges.py",
    output:
        "data/processed/export-manifest.json",
    shell:
        "uv run python -m mtor_nexus.graph.build"
