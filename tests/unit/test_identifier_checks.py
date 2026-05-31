"""Offline tests for identifier extraction and validation."""

import json
from pathlib import Path

from mtor_nexus.utils.doi_check import extract_dois
from mtor_nexus.utils.pdb_check import graph_pdb_ids
from mtor_nexus.utils.reproducibility import sha256_file
from mtor_nexus.utils.uniprot_check import graph_accessions

GRAPH_PATH = "data/processed/mtor-graph.json"


def test_seed_reference_dois_are_extractable() -> None:
    """Keep the bibliography parseable by the DOI CI job."""

    assert extract_dois("refs.bib") == [
        "10.1016/j.cell.2017.02.004",
        "10.1038/nature17963",
    ]


def test_required_uniprot_accessions_are_present() -> None:
    """Include the stable accession smoke-test set."""

    accessions = set(graph_accessions(GRAPH_PATH))
    assert {"P42345", "Q8N122", "Q6R327", "P49815", "Q15382"} <= accessions


def test_required_pdb_ids_are_present() -> None:
    """Include the structural identifier smoke-test set."""

    pdb_ids = set(graph_pdb_ids(GRAPH_PATH))
    assert {"5H64", "6ZWM", "6ZWO", "7DL2", "7UXH", "6CET"} <= pdb_ids


def test_seed_graph_provenance_digest_matches() -> None:
    """Keep the committed provenance ledger aligned with the seed bytes."""

    records = [
        json.loads(line)
        for line in Path("data/provenance.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    graph_record = [record for record in records if record["path"] == GRAPH_PATH][-1]
    assert graph_record["sha256"] == sha256_file(GRAPH_PATH)
