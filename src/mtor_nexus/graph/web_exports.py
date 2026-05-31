"""Generate deterministic browser assets for the Phase 3 visualization layer."""

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mtor_nexus.schema import MTOREdge, MTORNode

WEB_ROOT = "webapp/public/data"


@dataclass(frozen=True)
class ManuscriptModule:
    """One publication-oriented SBGN-PD diagram assembled from curation modules."""

    module_id: str
    slug: str
    title: str
    figure: str
    source_modules: tuple[str, ...]
    anchors: tuple[str, ...] = ()


MANUSCRIPT_MODULES = (
    ManuscriptModule(
        "1",
        "core-complex-architecture",
        "Core complex architecture",
        "Fig 1",
        ("01-core-complexes",),
    ),
    ManuscriptModule(
        "2",
        "growth-factor-pi3k-akt-tsc-rheb",
        "Growth factor -> PI3K-AKT -> TSC-Rheb -> mTORC1",
        "Fig 2",
        ("02-growth-factor-pi3k-akt", "03-tsc-rheb"),
        ("MTORC1",),
    ),
    ManuscriptModule(
        "3",
        "amino-acid-sensing",
        "Amino-acid sensing: Rag-Ragulator-GATOR-KICSTOR",
        "Fig 3",
        ("04-amino-acid-sensing",),
        ("MTORC1",),
    ),
    ManuscriptModule(
        "4",
        "energy-stress-sensing",
        "Energy and stress sensing",
        "Fig 4",
        ("05-energy-sensing", "06-stress-inputs"),
        ("MTORC1",),
    ),
    ManuscriptModule(
        "5",
        "protein-synthesis-autophagy",
        "Protein synthesis and autophagy outputs",
        "Fig 5",
        ("07-protein-synthesis", "08-autophagy"),
        ("MTORC1",),
    ),
    ManuscriptModule(
        "6",
        "mtorc2-outputs",
        "mTORC2 outputs",
        "Fig 6",
        ("10-mtorc2-outputs",),
        ("MTORC2",),
    ),
    ManuscriptModule(
        "7",
        "feedback-crosstalk",
        "Feedback and crosstalk",
        "Fig 7",
        ("11-feedback-crosstalk",),
        ("MTORC1", "AKT1"),
    ),
)


def _stable_fraction(identifier: str, axis: str) -> float:
    """Return a stable pseudorandom fraction for one identifier axis."""

    digest = hashlib.sha256(f"{identifier}:{axis}".encode()).hexdigest()
    return int(digest[:12], 16) / float(16**12)


def frozen_force_layout(nodes: list[MTORNode], edges: list[MTOREdge]) -> dict[str, Any]:
    """Compute a compact deterministic module-aware force layout."""

    modules = sorted({node.module for node in nodes})
    module_centers = {
        module: (
            76.0 * math.cos(index * math.tau / len(modules)),
            76.0 * math.sin(index * math.tau / len(modules)),
            26.0 * math.sin(index * math.tau * 2 / len(modules)),
        )
        for index, module in enumerate(modules)
    }
    positions: dict[str, list[float]] = {}
    for node in nodes:
        center = module_centers[node.module]
        positions[node.node_id] = [
            center[0] + (_stable_fraction(node.node_id, "x") - 0.5) * 34.0,
            center[1] + (_stable_fraction(node.node_id, "y") - 0.5) * 34.0,
            center[2] + (_stable_fraction(node.node_id, "z") - 0.5) * 34.0,
        ]
    links = [(edge.source, edge.target) for edge in edges]
    node_ids = [node.node_id for node in nodes]
    for _ in range(90):
        movement = {node_id: [0.0, 0.0, 0.0] for node_id in node_ids}
        for index, source_id in enumerate(node_ids):
            source = positions[source_id]
            for target_id in node_ids[index + 1 :]:
                target = positions[target_id]
                delta = [source[axis] - target[axis] for axis in range(3)]
                distance_squared = max(sum(value * value for value in delta), 5.0)
                scale = min(0.72, 42.0 / distance_squared)
                for axis in range(3):
                    force = delta[axis] * scale
                    movement[source_id][axis] += force
                    movement[target_id][axis] -= force
        for source_id, target_id in links:
            source = positions[source_id]
            target = positions[target_id]
            delta = [target[axis] - source[axis] for axis in range(3)]
            distance = max(math.sqrt(sum(value * value for value in delta)), 0.01)
            scale = (distance - 24.0) * 0.012
            for axis in range(3):
                force = delta[axis] / distance * scale
                movement[source_id][axis] += force
                movement[target_id][axis] -= force
        for node in nodes:
            center = module_centers[node.module]
            for axis in range(3):
                movement[node.node_id][axis] += (
                    center[axis] - positions[node.node_id][axis]
                ) * 0.012
                positions[node.node_id][axis] += max(-2.1, min(2.1, movement[node.node_id][axis]))
    return {
        "schema_version": "0.3.0",
        "layout": "deterministic-module-aware-force-relaxation",
        "nodes": [
            {
                "id": node.node_id,
                "x": round(positions[node.node_id][0], 4),
                "y": round(positions[node.node_id][1], 4),
                "z": round(positions[node.node_id][2], 4),
            }
            for node in nodes
        ],
    }


def _preset_position(index: int, count: int) -> dict[str, float]:
    """Return a deterministic concentric position for a Cytoscape node."""

    ring = int(math.sqrt(index))
    angle = index * 2.399963229728653
    radius = 74.0 + ring * 38.0 + (count % 5) * 2.0
    return {"x": round(math.cos(angle) * radius, 3), "y": round(math.sin(angle) * radius, 3)}


def _module_document(
    module: ManuscriptModule, nodes: list[MTORNode], edges: list[MTOREdge]
) -> dict[str, Any]:
    """Build one compact SBGN-PD Cytoscape document."""

    selected_ids = {node.node_id for node in nodes if node.module in module.source_modules} | set(
        module.anchors
    )
    selected_nodes = sorted(
        (node for node in nodes if node.node_id in selected_ids), key=lambda node: node.node_id
    )
    selected_edges = [
        edge for edge in edges if edge.source in selected_ids and edge.target in selected_ids
    ]
    return {
        "schema_version": "0.3.0",
        "module": {
            "id": module.module_id,
            "slug": module.slug,
            "title": module.title,
            "figure": module.figure,
            "source_modules": list(module.source_modules),
        },
        "elements": {
            "nodes": [
                {
                    "data": {"id": node.node_id, **node.model_dump(mode="json")},
                    "position": _preset_position(index, len(selected_nodes)),
                }
                for index, node in enumerate(selected_nodes)
            ],
            "edges": [
                {"data": {"id": f"m{module.module_id}-e{index}", **edge.model_dump(mode="json")}}
                for index, edge in enumerate(selected_edges)
            ],
        },
    }


def write_web_exports(nodes: list[MTORNode], edges: list[MTOREdge], root: str = WEB_ROOT) -> None:
    """Write every committed browser artifact used by the Phase 3 app."""

    output = Path(root)
    module_output = output / "modules"
    module_output.mkdir(parents=True, exist_ok=True)
    for stale_module in module_output.glob("*.json"):
        stale_module.unlink()
    document = {
        "schema_version": "0.3.0",
        "nodes": [node.model_dump(mode="json") for node in nodes],
        "edges": [edge.model_dump(mode="json") for edge in edges],
    }
    (output / "mtor-graph.json").write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "mtor-3d-layout.json").write_text(
        json.dumps(frozen_force_layout(nodes, edges), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    citations = {
        doi: {
            "doi": doi,
            "title": "Curated mTOR pathway reference",
            "url": f"https://doi.org/{doi}",
        }
        for doi in sorted(
            {citation for node in nodes for citation in node.primary_citations}
            | {citation for edge in edges for citation in edge.citations}
        )
    }
    (output / "citations.json").write_text(
        json.dumps(citations, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for module in MANUSCRIPT_MODULES:
        (module_output / f"{module.module_id}.json").write_text(
            json.dumps(_module_document(module, nodes, edges), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
