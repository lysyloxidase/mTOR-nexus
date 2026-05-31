"""Load and validate the normalized Phase 1 graph."""

import json
from pathlib import Path
from typing import Any

from mtor_nexus.schema import MTOREdge, MTORNode
from mtor_nexus.utils.nomenclature import validate_nomenclature


def load_graph(path: str) -> dict[str, Any]:
    """Read a normalized JSON graph document."""

    with Path(path).open(encoding="utf-8") as graph_file:
        graph: dict[str, Any] = json.load(graph_file)
    return graph


def validate_graph(path: str) -> tuple[list[MTORNode], list[MTOREdge]]:
    """Validate nodes, edges, endpoint references, and nomenclature guards."""

    graph = load_graph(path)
    nodes = [MTORNode.model_validate(node) for node in graph["nodes"]]
    edges = [MTOREdge.model_validate(edge) for edge in graph["edges"]]
    node_ids = {node.node_id for node in nodes}
    unknown_ids = {
        endpoint
        for edge in edges
        for endpoint in (edge.source, edge.target)
        if endpoint not in node_ids
    }
    if unknown_ids:
        raise ValueError(f"edge endpoints missing from node set: {sorted(unknown_ids)}")
    validate_nomenclature(nodes, edges)
    return nodes, edges
