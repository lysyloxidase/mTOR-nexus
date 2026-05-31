"""CLI validator for graph evidence tiers and species provenance."""

import argparse

from mtor_nexus.utils.graph_io import validate_graph


def main() -> int:
    """Validate the normalized graph from the command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="data/processed/mtor-graph.json")
    args = parser.parse_args()
    nodes, edges = validate_graph(args.graph)
    print(f"validated {len(nodes)} node(s) and {len(edges)} edge(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
