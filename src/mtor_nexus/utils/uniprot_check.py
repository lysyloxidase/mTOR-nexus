"""Validate graph UniProt accessions against the UniProt REST API."""

import argparse
import re
from concurrent.futures import ThreadPoolExecutor

from mtor_nexus.utils.graph_io import load_graph
from mtor_nexus.utils.http_check import resolves

UNIPROT_ACCESSION_PATTERN = re.compile(r"^[A-Z0-9]{6,10}$")
UNIPROT_ENTRY_URL = "https://rest.uniprot.org/uniprotkb/{accession}.json"


def _accession_resolves(accession: str) -> bool:
    """Resolve one accession against UniProt."""

    return resolves(UNIPROT_ENTRY_URL.format(accession=accession))


def graph_accessions(graph_path: str) -> list[str]:
    """Collect unique UniProt accessions from a normalized graph."""

    graph = load_graph(graph_path)
    return sorted({node["uniprot_id"] for node in graph["nodes"] if node.get("uniprot_id")})


def broken_accessions(accessions: list[str]) -> list[str]:
    """Return malformed or unresolved UniProt accessions."""

    malformed = [
        accession for accession in accessions if not UNIPROT_ACCESSION_PATTERN.fullmatch(accession)
    ]
    candidates = [accession for accession in accessions if accession not in malformed]
    with ThreadPoolExecutor(max_workers=12) as executor:
        resolution = executor.map(_accession_resolves, candidates)
    unresolved = [
        accession for accession, valid in zip(candidates, resolution, strict=True) if not valid
    ]
    return sorted([*malformed, *unresolved])


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
