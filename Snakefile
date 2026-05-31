"""Phase 2 data-ingestion DAG placeholder."""

rule all:
    input:
        "data/processed/mtor-graph.json"


rule seed_graph:
    output:
        "data/processed/mtor-graph.json"
    message:
        "The curated Phase 1 seed graph is committed; Phase 2 loaders will regenerate it."
    shell:
        "test -f {output}"
