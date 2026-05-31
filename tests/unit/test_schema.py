"""Graph schema contract tests."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mtor_nexus.schema import MTOREdge, MTORNode
from mtor_nexus.utils.graph_io import validate_graph

GRAPH_PATH = "data/processed/mtor-graph.json"


def test_pathway_graph_round_trips() -> None:
    """Validate the curated Phase 2 graph and its minimum useful size."""

    nodes, edges = validate_graph(GRAPH_PATH)
    assert len(nodes) >= 215
    assert len(edges) >= 220
    assert all(MTORNode.model_validate_json(node.model_dump_json()) == node for node in nodes)
    assert all(MTOREdge.model_validate_json(edge.model_dump_json()) == edge for edge in edges)


@pytest.mark.parametrize(
    "missing_field", ["tier", "species_evidence", "evidence_sources", "source_refs"]
)
def test_edges_require_tier_and_species_evidence(missing_field: str) -> None:
    """Reject edges that omit either mandatory evidence dimension."""

    graph = json.loads(Path(GRAPH_PATH).read_text(encoding="utf-8"))
    edge = graph["edges"][0]
    edge.pop(missing_field)
    with pytest.raises(ValidationError):
        MTOREdge.model_validate(edge)


def test_species_evidence_cannot_be_empty() -> None:
    """Require at least one provenance flag per edge."""

    graph = json.loads(Path(GRAPH_PATH).read_text(encoding="utf-8"))
    edge = graph["edges"][0]
    edge["species_evidence"] = []
    with pytest.raises(ValidationError):
        MTOREdge.model_validate(edge)


def test_phosphorylation_edges_require_site_identifier() -> None:
    """Require resolvable PhosphoSitePlus references for phosphorylation."""

    graph = json.loads(Path(GRAPH_PATH).read_text(encoding="utf-8"))
    edge = graph["edges"][0]
    edge.pop("phosphositeplus_id")
    with pytest.raises(ValidationError):
        MTOREdge.model_validate(edge)


def test_all_edge_endpoints_exist() -> None:
    """Prevent dangling references in normalized graph exports."""

    nodes, edges = validate_graph(GRAPH_PATH)
    node_ids = {node.node_id for node in nodes}
    assert all(edge.source in node_ids and edge.target in node_ids for edge in edges)
