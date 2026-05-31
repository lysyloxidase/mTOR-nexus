"""Validate graph UniProt accessions against the UniProt REST API."""

import argparse
import re

from mtor_nexus.utils.graph_io import load_graph
from mtor_nexus.utils.http_check import resolves

UNIPROT_ACCESSION_PATTERN = re.compile(r"^[A-Z0-9]{6,10}$")
UNIPROT_ENTRY_URL = "https://rest.uniprot.org/uniprotkb/{accession}.json"


def graph_accessions(graph_path: str) -> list[str]:
    """Collect unique UniProt accessions from a normalized graph."""

    graph = load_graph(graph_path)
    return sorted({node["uniprot_id"] for node in graph["nodes"] if node.get("uniprot_id")})


def broken_accessions(accessions: list[str]) -> list[str]:
    """Return malformed or unresolved UniProt accessions."""

    return [
        accession
        for accession in accessions
        if not UNIPROT_ACCESSION_PATTERN.fullmatch(accession)
        or not resolves(UNIPROT_ENTRY_URL.format(accession=accession))
    ]


def main() -> int:
    """Run UniProt validation from the command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="data/processed/mtor-graph.json")
    args = parser.parse_args()
    accessions = graph_accessions(args.graph)
    failures = broken_accessions(accessions)
    print(f"checked {len(accessions)} UniProt accession(s); broken: {len(failures)}")
    for accession in failures:
        print(f"BROKEN UNIPROT: {accession}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
