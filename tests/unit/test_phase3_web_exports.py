"""Validate deterministic Phase 3 browser exports."""

import json
from pathlib import Path

from mtor_nexus.graph.build import MTORGraphBuilder
from mtor_nexus.graph.web_exports import MANUSCRIPT_MODULES, write_web_exports


def test_web_exports_cover_graph_and_seven_modules(tmp_path: Path) -> None:
    """Browser assets preserve global IDs and create seven manuscript diagrams."""

    graph = MTORGraphBuilder().build()
    root = tmp_path / "web"
    write_web_exports(graph.nodes, graph.edges, str(root))
    browser_graph = json.loads((root / "mtor-graph.json").read_text(encoding="utf-8"))
    layout = json.loads((root / "mtor-3d-layout.json").read_text(encoding="utf-8"))

    assert len(browser_graph["nodes"]) == len(graph.nodes)
    assert len(browser_graph["edges"]) == len(graph.edges)
    assert {node["id"] for node in layout["nodes"]} == {node.node_id for node in graph.nodes}
    assert sorted(path.name for path in (root / "modules").glob("*.json")) == [
        f"{module.module_id}.json" for module in MANUSCRIPT_MODULES
    ]


def test_committed_web_modules_share_global_node_ids() -> None:
    """Committed Cytoscape documents retain canonical graph identifiers."""

    graph = json.loads(Path("webapp/public/data/mtor-graph.json").read_text(encoding="utf-8"))
    graph_ids = {node["node_id"] for node in graph["nodes"]}
    for module in MANUSCRIPT_MODULES:
        document = json.loads(
            Path(f"webapp/public/data/modules/{module.module_id}.json").read_text(encoding="utf-8")
        )
        assert document["elements"]["nodes"]
        assert {node["data"]["node_id"] for node in document["elements"]["nodes"]} <= graph_ids
