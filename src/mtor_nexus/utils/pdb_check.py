"""Validate graph PDB IDs against the RCSB PDB REST API."""

import argparse
import re
from concurrent.futures import ThreadPoolExecutor

from mtor_nexus.utils.graph_io import load_graph
from mtor_nexus.utils.http_check import resolves

PDB_ID_PATTERN = re.compile(r"^[0-9][A-Z0-9]{3}$")
PDB_ENTRY_URL = "https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"


def _pdb_id_resolves(pdb_id: str) -> bool:
    """Resolve one identifier against RCSB PDB."""

    return resolves(PDB_ENTRY_URL.format(pdb_id=pdb_id))


def graph_pdb_ids(graph_path: str) -> list[str]:
    """Collect unique PDB IDs from a normalized graph."""

    graph = load_graph(graph_path)
    return sorted({pdb_id.upper() for node in graph["nodes"] for pdb_id in node.get("pdb_ids", [])})


def broken_pdb_ids(pdb_ids: list[str]) -> list[str]:
    """Return malformed or unresolved PDB identifiers."""

    malformed = [pdb_id for pdb_id in pdb_ids if not PDB_ID_PATTERN.fullmatch(pdb_id)]
    candidates = [pdb_id for pdb_id in pdb_ids if pdb_id not in malformed]
    with ThreadPoolExecutor(max_workers=12) as executor:
        resolution = executor.map(_pdb_id_resolves, candidates)
    unresolved = [pdb_id for pdb_id, valid in zip(candidates, resolution, strict=True) if not valid]
    return sorted([*malformed, *unresolved])


def main() -> int:
    """Run PDB validation from the command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="data/processed/mtor-graph.json")
    args = parser.parse_args()
    pdb_ids = graph_pdb_ids(args.graph)
    failures = broken_pdb_ids(pdb_ids)
    print(f"checked {len(pdb_ids)} PDB ID(s); broken: {len(failures)}")
    for pdb_id in failures:
        print(f"BROKEN PDB: {pdb_id}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
