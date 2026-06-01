# pyright: reportMissingTypeStubs=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""Build and export the Phase 2 heterogeneous mTOR pathway graph."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import pyarrow as pa
import pyarrow.parquet as pq
from neo4j import GraphDatabase

from mtor_nexus.graph.catalog import (
    DRUG_SEEDS,
    NON_PROTEIN_SEEDS,
    ProteinSeed,
    SAxton_2017,
    protein_seeds,
)
from mtor_nexus.graph.curated_edges import curated_edges
from mtor_nexus.ingest.source_registry import load_source_registry
from mtor_nexus.schema import MTOREdge, MTORNode
from mtor_nexus.utils.reproducibility import sha256_file

DEFAULT_ACCESSIONS = "data/curated/uniprot-accessions.json"
DEFAULT_JSON = "data/processed/mtor-graph.json"
BIOSCHEMAS_CONTEXT = {
    "@vocab": "https://w3id.org/mtor-nexus/schema/",
    "bioschemas": "https://bioschemas.org/",
    "citations": "http://purl.org/dc/terms/references",
    "node_id": "@id",
}


@dataclass(frozen=True)
class HeteroData:
    """Dependency-light heterogeneous graph container for atlas services."""

    nodes: list[MTORNode]
    edges: list[MTOREdge]
    metadata: dict[str, Any]

    def document(self) -> dict[str, Any]:
        """Serialize the normalized graph document."""

        return {
            "@context": BIOSCHEMAS_CONTEXT,
            "schema_version": "0.2.0",
            "metadata": self.metadata,
            "nodes": [node.model_dump(mode="json") for node in self.nodes],
            "edges": [edge.model_dump(mode="json") for edge in self.edges],
        }


class MTORGraphBuilder:
    """Construct and export the curated Phase 2 mTOR pathway graph."""

    def __init__(self, accession_path: str = DEFAULT_ACCESSIONS) -> None:
        """Load the committed derived UniProt accession snapshot."""

        self.accession_path = Path(accession_path)
        self.accessions: dict[str, str] = json.loads(
            self.accession_path.read_text(encoding="utf-8")
        )
        self.graph: HeteroData | None = None

    def _protein_node(self, seed: ProteinSeed) -> MTORNode:
        """Expand one compact protein seed into the normalized schema."""

        return MTORNode(
            node_id=seed.symbol,
            gene_symbol=seed.symbol,
            protein_name=seed.symbol,
            uniprot_id=self.accessions[seed.symbol],
            node_type=seed.node_type,
            pathway_role=seed.role,
            localization=list(seed.localization),
            domains=list(seed.domains),
            pdb_ids=list(seed.pdb_ids),
            complex_membership=list(seed.membership),
            aliases=list(seed.aliases),
            module=seed.module,
            source_refs=[f"uniprot:{self.accessions[seed.symbol]}"],
            primary_citations=[SAxton_2017],
        )

    def build(self) -> HeteroData:
        """Construct the normalized graph and check endpoint integrity."""

        nodes = [self._protein_node(seed) for seed in protein_seeds()]
        nodes.extend(
            MTORNode(
                node_id=seed.node_id,
                protein_name=seed.node_id,
                chebi_id=seed.chebi_id,
                chembl_id=seed.chembl_id,
                node_type=seed.node_type,
                pathway_role=seed.role,
                localization=list(seed.localization),
                pdb_ids=list(seed.pdb_ids),
                complex_membership=list(seed.membership),
                aliases=list(seed.aliases),
                module=seed.module,
                source_refs=list(seed.source_refs),
                primary_citations=[SAxton_2017],
            )
            for seed in [*NON_PROTEIN_SEEDS, *DRUG_SEEDS]
        )
        edges = curated_edges()
        node_ids = {node.node_id for node in nodes}
        unknown = {
            endpoint
            for edge in edges
            for endpoint in (edge.source, edge.target)
            if endpoint not in node_ids
        }
        if unknown:
            raise ValueError(f"edge endpoints missing from catalog: {sorted(unknown)}")
        registry = load_source_registry()
        self.graph = HeteroData(
            nodes=nodes,
            edges=edges,
            metadata={
                "title": "mTOR-NEXUS Phase 2 curated pathway graph",
                "source_versions": {name: source.version for name, source in registry.items()},
                "reactome_root": registry["reactome"].options["pathway_root"],
                "kegg_pathway": registry["kegg"].options["pathway"],
                "phosphositeplus_raw_redistributed": False,
            },
        )
        return self.graph

    def _require_graph(self) -> HeteroData:
        """Return a built graph or construct it lazily."""

        return self.graph or self.build()

    def to_json(self, path: str = DEFAULT_JSON) -> None:
        """Write the canonical normalized JSON document."""

        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(self._require_graph().document(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def to_parquet(self, path: str) -> None:
        """Write separate node and edge Parquet tables."""

        output = Path(path)
        output.mkdir(parents=True, exist_ok=True)
        graph = self._require_graph()
        pq.write_table(
            pa.Table.from_pylist([node.model_dump(mode="json") for node in graph.nodes]),
            output / "nodes.parquet",
        )
        pq.write_table(
            pa.Table.from_pylist([edge.model_dump(mode="json") for edge in graph.edges]),
            output / "edges.parquet",
        )

    def to_graphml(self, path: str) -> None:
        """Write a portable GraphML representation."""

        graphml = ElementTree.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
        for key, scope in [
            ("module", "node"),
            ("node_type", "node"),
            ("uniprot_id", "node"),
            ("mechanism", "edge"),
            ("tier", "edge"),
            ("species_evidence", "edge"),
        ]:
            ElementTree.SubElement(
                graphml,
                "key",
                {"id": key, "for": scope, "attr.name": key, "attr.type": "string"},
            )
        graph = ElementTree.SubElement(graphml, "graph", edgedefault="directed")
        for node in self._require_graph().nodes:
            element = ElementTree.SubElement(graph, "node", id=node.node_id)
            self._xml_data(element, "module", node.module)
            self._xml_data(element, "node_type", node.node_type.value)
            self._xml_data(element, "uniprot_id", node.uniprot_id or "")
        for index, edge in enumerate(self._require_graph().edges):
            element = ElementTree.SubElement(
                graph,
                "edge",
                id=f"e{index}",
                source=edge.source,
                target=edge.target,
            )
            self._xml_data(element, "mechanism", edge.mechanism.value)
            self._xml_data(element, "tier", edge.tier.value)
            self._xml_data(element, "species_evidence", json.dumps(edge.species_evidence))
        self._write_xml(path, graphml)

    @staticmethod
    def _xml_data(parent: ElementTree.Element, key: str, value: str) -> None:
        """Append one GraphML data field."""

        data = ElementTree.SubElement(parent, "data", key=key)
        data.text = value

    @staticmethod
    def _write_xml(path: str, root: ElementTree.Element) -> None:
        """Write an XML artifact with a declaration."""

        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        ElementTree.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)

    def to_jsonld(self, path: str) -> None:
        """Write a FAIR JSON-LD graph using Bioschemas type references."""

        graph = self._require_graph()
        document = {
            "@context": BIOSCHEMAS_CONTEXT,
            "@graph": [
                {
                    "@id": node.node_id,
                    "@type": "bioschemas:BioChemEntity",
                    **node.model_dump(mode="json"),
                }
                for node in graph.nodes
            ]
            + [
                {
                    "@id": f"edge:{index}",
                    "@type": "bioschemas:Study",
                    **edge.model_dump(mode="json"),
                }
                for index, edge in enumerate(graph.edges)
            ],
        }
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def to_cytoscape_json(self, module: str, path: str) -> None:
        """Write one module-focused Cytoscape JSON export."""

        graph = self._require_graph()
        selected_nodes = {node.node_id for node in graph.nodes if node.module == module}
        selected_edges = [
            edge
            for edge in graph.edges
            if edge.source in selected_nodes or edge.target in selected_nodes
        ]
        selected_nodes.update(edge.source for edge in selected_edges)
        selected_nodes.update(edge.target for edge in selected_edges)
        document = {
            "elements": {
                "nodes": [
                    {"data": node.model_dump(mode="json")}
                    for node in graph.nodes
                    if node.node_id in selected_nodes
                ],
                "edges": [
                    {"data": {"id": f"e{index}", **edge.model_dump(mode="json")}}
                    for index, edge in enumerate(selected_edges)
                ],
            }
        }
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def to_neo4j(self, uri: str, auth: tuple[str, str], *, clear: bool = False) -> None:
        """Load nodes and typed relationships into Neo4j."""

        graph = self._require_graph()
        with GraphDatabase.driver(uri, auth=auth) as driver:
            driver.verify_connectivity()
            with driver.session() as session:
                if clear:
                    session.run("MATCH (n) DETACH DELETE n").consume()
                session.run(
                    "CREATE CONSTRAINT mtor_node_id IF NOT EXISTS "
                    "FOR (n:MTORNode) REQUIRE n.node_id IS UNIQUE"
                ).consume()
                session.run(
                    "UNWIND $nodes AS node "
                    "MERGE (n:MTORNode {node_id: node.node_id}) "
                    "SET n += node",
                    nodes=[
                        self._neo4j_properties(node.model_dump(mode="json")) for node in graph.nodes
                    ],
                ).consume()
                for edge in graph.edges:
                    relation = edge.mechanism.value.upper()
                    session.run(
                        f"MATCH (source:MTORNode {{node_id: $source}}), "
                        f"(target:MTORNode {{node_id: $target}}) "
                        f"CREATE (source)-[r:{relation}]->(target) SET r += $properties",
                        source=edge.source,
                        target=edge.target,
                        properties=self._neo4j_properties(edge.model_dump(mode="json")),
                    ).consume()

    @staticmethod
    def _neo4j_properties(properties: dict[str, Any]) -> dict[str, Any]:
        """Drop nulls and encode nested values for Neo4j property storage."""

        normalized: dict[str, Any] = {}
        for key, value in properties.items():
            if value is None:
                continue
            normalized[key] = value if isinstance(value, str | int | float | bool) else list(value)
        return normalized

    def write_all(self, root: str = "data/processed") -> None:
        """Generate every committed graph and overlay exchange format."""

        graph = self._require_graph()
        root_path = Path(root)
        self.to_json(str(root_path / "mtor-graph.json"))
        self.to_parquet(str(root_path / "parquet"))
        self.to_graphml(str(root_path / "mtor-graph.graphml"))
        self.to_jsonld(str(root_path / "mtor-graph.jsonld"))
        cytoscape_path = root_path / "cytoscape"
        cytoscape_path.mkdir(parents=True, exist_ok=True)
        for stale_export in cytoscape_path.glob("*.json"):
            stale_export.unlink()
        for module in sorted({node.module for node in graph.nodes}):
            self.to_cytoscape_json(module, str(cytoscape_path / f"{module}.json"))
        from mtor_nexus.disease.export import write_disease_exports

        write_disease_exports(processed_path=str(root_path / "disease-layer.json"))
        artifact_paths = sorted(
            path
            for path in root_path.rglob("*")
            if path.is_file() and path.name != "export-manifest.json"
        )
        (root_path / "export-manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": "0.2.0",
                    "artifacts": {
                        str(path.relative_to(root_path)): sha256_file(str(path))
                        for path in artifact_paths
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        from mtor_nexus.graph.web_exports import write_web_exports

        write_web_exports(graph.nodes, graph.edges)


def main() -> int:
    """Build all normalized graph exports."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/processed")
    args = parser.parse_args()
    builder = MTORGraphBuilder()
    graph = builder.build()
    builder.write_all(args.root)
    print(f"exported {len(graph.nodes)} nodes and {len(graph.edges)} edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
