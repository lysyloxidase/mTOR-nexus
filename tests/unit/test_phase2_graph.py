"""Phase 2 inventory, evidence, and reconciliation tests."""

import json
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

import pyarrow.parquet as pq
import pytest

from mtor_nexus.graph.build import MTORGraphBuilder
from mtor_nexus.graph.catalog import AUTOPHAGY, DRUGS
from mtor_nexus.graph.validate import validate_phase2_graph
from mtor_nexus.ingest.live_probe import probe_kegg, probe_reactome, probe_string
from mtor_nexus.ingest.source_index import build_source_index
from mtor_nexus.ingest.source_registry import load_source_registry, restricted_sources
from mtor_nexus.schema import EdgeMechanism, NodeType, RecruitmentMode
from mtor_nexus.utils.graph_io import validate_graph
from mtor_nexus.utils.reproducibility import sha256_file

GRAPH_PATH = "data/processed/mtor-graph.json"


def test_phase2_release_metrics() -> None:
    """Keep the committed graph inside the registered Phase 2 bands."""

    report = validate_phase2_graph(GRAPH_PATH)
    assert report.node_count >= 215
    assert report.mechanism_counts["phosphorylates"] >= 70
    assert report.reactome_reconciliation >= 0.90
    assert report.kegg_reconciliation >= 0.85
    assert report.single_source_edges == 0
    assert report.rodent_only_ratio == pytest.approx(0.20, abs=0.05)
    assert report.tier_distribution["robust"] == pytest.approx(0.55, abs=0.05)
    assert report.tier_distribution["plausible"] == pytest.approx(0.35, abs=0.05)
    assert report.tier_distribution["speculative"] == pytest.approx(0.10, abs=0.05)


def test_identifier_requirements_by_node_type() -> None:
    """Require stable identifiers for proteins, drugs, metabolites, and lipids."""

    nodes, _ = validate_graph(GRAPH_PATH)
    assert all(node.uniprot_id for node in nodes if node.gene_symbol)
    assert all(node.chembl_id for node in nodes if node.node_type == NodeType.SMALL_MOLECULE)
    assert all(
        node.chebi_id for node in nodes if node.node_type in {NodeType.METABOLITE, NodeType.LIPID}
    )


def test_phosphorylation_edges_have_site_grounding() -> None:
    """Keep every phospho edge linked to a segregated PSP identifier and DOI."""

    _, edges = validate_graph(GRAPH_PATH)
    phospho_edges = [edge for edge in edges if edge.mechanism == EdgeMechanism.PHOSPHORYLATES]
    assert len(phospho_edges) >= 70
    assert all(edge.phosphositeplus_id for edge in phospho_edges)
    assert all(
        any(citation.startswith("10.") for citation in edge.citations) for edge in phospho_edges
    )


def test_three_recruitment_modes_are_represented() -> None:
    """Protect TOS, mSIN1, and FLCN-RagC-GDP recruitment semantics."""

    _, edges = validate_graph(GRAPH_PATH)
    recruitment = Counter(edge.recruitment_mode for edge in edges)
    assert recruitment[RecruitmentMode.TOS_MOTIF] >= 3
    assert recruitment[RecruitmentMode.MSIN1] >= 3
    assert recruitment[RecruitmentMode.FLCN_RAGC_GDP] >= 1
    assert any(
        edge.source == "FLCN"
        and edge.target == "TFEB"
        and edge.recruitment_mode == RecruitmentMode.FLCN_RAGC_GDP
        for edge in edges
    )


def test_all_exchange_formats_are_exported(tmp_path: Path) -> None:
    """Write Parquet, GraphML, JSON-LD, and module Cytoscape exports."""

    builder = MTORGraphBuilder()
    graph = builder.build()
    builder.to_parquet(str(tmp_path / "parquet"))
    builder.to_graphml(str(tmp_path / "graph.graphml"))
    builder.to_jsonld(str(tmp_path / "graph.jsonld"))
    builder.to_cytoscape_json(AUTOPHAGY, str(tmp_path / "autophagy.json"))
    assert pq.read_table(tmp_path / "parquet" / "nodes.parquet").num_rows == len(graph.nodes)
    assert pq.read_table(tmp_path / "parquet" / "edges.parquet").num_rows == len(graph.edges)
    assert ElementTree.parse(tmp_path / "graph.graphml").getroot().tag.endswith("graphml")
    assert json.loads((tmp_path / "graph.jsonld").read_text(encoding="utf-8"))["@graph"]
    assert json.loads((tmp_path / "autophagy.json").read_text(encoding="utf-8"))["elements"][
        "nodes"
    ]


def test_committed_export_manifest_matches_artifacts() -> None:
    """Keep committed exchange artifacts byte-for-byte reproducible."""

    manifest = json.loads(Path("data/processed/export-manifest.json").read_text(encoding="utf-8"))
    for relative_path, digest in manifest["artifacts"].items():
        assert sha256_file(str(Path("data/processed") / relative_path)) == digest


def test_source_registry_segregates_phosphositeplus() -> None:
    """Keep non-commercial PSP raw records outside open exports."""

    registry = load_source_registry()
    assert restricted_sources(registry) == {"phosphositeplus"}
    index = build_source_index()
    assert index["segregated_raw_sources"] == ["phosphositeplus"]
    assert index["derived_artifacts"]["uniprot_accessions"]["record_count"] >= 200


def test_catalog_includes_drug_module() -> None:
    """Keep the Phase 5 seed pharmacology surface available in Phase 2."""

    nodes, _ = validate_graph(GRAPH_PATH)
    assert sum(node.module == DRUGS for node in nodes) >= 20


def test_live_probe_parsers_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Parse public overlay responses without depending on endpoint uptime."""

    def fake_read(url: str) -> bytes:
        if "kegg" in url:
            return b"<pathway><relation/><relation/></pathway>"
        return b'[{"stId":"R-HSA-1"},{"stId":"R-HSA-2"}]'

    monkeypatch.setattr("mtor_nexus.ingest.live_probe._read", fake_read)
    assert probe_kegg().record_count == 2
    assert probe_reactome().record_count == 2
    assert probe_string().record_count == 1
