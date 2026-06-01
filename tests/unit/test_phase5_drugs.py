"""Validate the Phase 5 inhibitor pharmacology and training layer."""

import json
import sys
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError

import pytest
from pydantic import ValidationError

from mtor_nexus.disease.validate import main as disease_validate_main
from mtor_nexus.drugs import bioactivity
from mtor_nexus.drugs.bioactivity import (
    load_bioactivity_snapshot,
    refresh_bioactivity_snapshot,
    smiles_is_parseable,
    standardize_smiles,
)
from mtor_nexus.drugs.catalog import COUNTER_SCREEN_TARGETS, DRUGS, drug_by_name, drug_target_links
from mtor_nexus.drugs.export import drug_document, write_drug_exports
from mtor_nexus.drugs.models import AssayMetadata, DrugDocument
from mtor_nexus.drugs.validate import main as validate_main
from mtor_nexus.drugs.validate import validate_phase5_layer
from mtor_nexus.graph.build import MTORGraphBuilder
from mtor_nexus.graph.validate import main as graph_validate_main
from mtor_nexus.ingest.source_index import main as source_index_main


def test_phase5_release_metrics() -> None:
    """Protect catalog, mechanism-edge, counter-screen, and resistance coverage."""

    report = validate_phase5_layer()
    assert report.generation_count == 5
    assert report.drug_count == 23
    assert report.target_link_count == 27
    assert report.counter_screen_target_count == 5
    assert report.bioactivity_label_count == 275
    assert report.compounds_with_labels == 16
    assert report.resistance_mutation_count == 3


@pytest.mark.parametrize("name", ["sapanisertib", "MLN0128", "INK128", "TAK-228", "TAK228"])
def test_sapanisertib_aliases_resolve_to_one_node(name: str) -> None:
    """Unify punctuation and case variants into the canonical drug record."""

    assert drug_by_name(name) is DRUGS["sapanisertib"]


def test_unknown_drug_alias_is_rejected() -> None:
    """Do not silently materialize an unknown compound name."""

    with pytest.raises(KeyError, match="unknown inhibitor alias"):
        drug_by_name("not-a-real-inhibitor")


def test_counter_screen_snapshot_has_rdkit_structures_and_all_targets() -> None:
    """Retain parseable structures and explicit PIKK counter-screen labels."""

    compounds = load_bioactivity_snapshot()
    activities = [activity for compound in compounds for activity in compound.activities]
    assert {compound.drug_id for compound in compounds} == set(DRUGS)
    assert {activity.target_gene_symbol for activity in activities} == {
        "MTOR",
        "PIK3CA",
        "ATM",
        "ATR",
        "PRKDC",
    }
    assert {target.chembl_id for target in COUNTER_SCREEN_TARGETS} >= {"CHEMBL2842", "CHEMBL4005"}
    assert all(compound.rdkit_standardized_smiles for compound in compounds)


def test_standardize_smiles_rejects_unparseable_input() -> None:
    """Surface malformed upstream structures rather than shipping them."""

    with pytest.raises(ValueError, match="RDKit"):
        standardize_smiles("not-smiles")
    assert smiles_is_parseable("CC")


def test_drug_target_edges_are_tiered_and_species_tagged() -> None:
    """Keep every inhibitor connected to pathway nodes with evidence tags."""

    links = drug_target_links()
    assert {link.drug_id for link in links} == set(DRUGS)
    assert all(link.tier and link.species_evidence for link in links)
    assert {link.target_node_id for link in links if link.drug_id == "dactolisib"} == {
        "MTOR",
        "PIK3CA",
    }


def test_drug_export_is_browser_ready(tmp_path: Path) -> None:
    """Write identical analysis and browser pharmacology overlays."""

    processed = tmp_path / "processed.json"
    web = tmp_path / "web.json"
    write_drug_exports(str(processed), str(web))
    document = drug_document()
    assert json.loads(processed.read_text(encoding="utf-8")) == document
    assert json.loads(web.read_text(encoding="utf-8")) == document


def test_refresh_parser_without_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Refresh a compact mocked ChEMBL response without endpoint uptime."""

    monkeypatch.setattr(
        "mtor_nexus.drugs.bioactivity._activity_rows",
        lambda: [
            {
                "activity_id": 1,
                "molecule_chembl_id": "CHEMBL413",
                "target_chembl_id": "CHEMBL2842",
                "standard_type": "IC50",
                "standard_relation": "=",
                "standard_value": "1.5",
                "standard_units": "nM",
                "assay_chembl_id": "CHEMBL1",
                "assay_description": "Mock assay",
                "assay_type": "B",
            },
            {
                "activity_id": 2,
                "molecule_chembl_id": "CHEMBL413",
                "target_chembl_id": "CHEMBL2842",
                "standard_type": "IC50",
                "standard_relation": "=",
                "standard_value": None,
                "standard_units": "nM",
                "assay_chembl_id": "CHEMBL1",
                "assay_description": "Ignored mock assay",
                "assay_type": "B",
            },
        ],
    )
    monkeypatch.setattr(
        "mtor_nexus.drugs.bioactivity._assay_metadata",
        lambda *_args: AssayMetadata(
            assay_chembl_id="CHEMBL1",
            assay_type="B",
            description="Mock assay",
            confidence_score=9,
        ),
    )
    monkeypatch.setattr(
        "mtor_nexus.drugs.bioactivity._read_json",
        lambda _url: {"molecule_structures": {"canonical_smiles": "CC"}},
    )
    compounds = refresh_bioactivity_snapshot(str(tmp_path / "snapshot.json"))
    assert len(compounds) == len(DRUGS)
    assert compounds[0].activities[0].standard_value == 1.5


def test_read_json_retries_transient_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Retry public API failures before accepting a JSON response."""

    responses: list[BytesIO | HTTPError] = [
        HTTPError("https://example.test", 500, "temporary", None, None),
        BytesIO(b'{"ok": true}'),
    ]

    def fake_urlopen(_url: str, timeout: int) -> BytesIO:
        assert timeout == 60
        response = responses.pop(0)
        if isinstance(response, HTTPError):
            raise response
        return response

    monkeypatch.setattr(bioactivity, "urlopen", fake_urlopen)
    monkeypatch.setattr(bioactivity.time, "sleep", lambda _seconds: None)
    assert bioactivity._read_json("https://example.test") == {"ok": True}


def test_read_json_surfaces_persistent_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Surface public API failures after the bounded retry budget."""

    def fail(_url: str, timeout: int) -> BytesIO:
        assert timeout == 60
        raise HTTPError("https://example.test", 500, "persistent", None, None)

    monkeypatch.setattr(bioactivity, "urlopen", fail)
    monkeypatch.setattr(bioactivity.time, "sleep", lambda _seconds: None)
    with pytest.raises(HTTPError):
        bioactivity._read_json("https://example.test")


def test_assay_metadata_cache_and_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cache detailed assay metadata and retain feed metadata on legacy API failures."""

    monkeypatch.setattr(
        bioactivity,
        "_read_json",
        lambda _url: {
            "assay_type": "B",
            "description": "Detailed assay",
            "confidence_score": 9,
        },
    )
    cache: dict[str, AssayMetadata] = {}
    assert bioactivity._assay_metadata("CHEMBL1", "Feed assay", "F", cache).confidence_score == 9
    assert (
        bioactivity._assay_metadata("CHEMBL1", "Ignored", "F", cache).description
        == "Detailed assay"
    )

    def fail(_url: str) -> dict[str, object]:
        raise HTTPError("https://example.test", 500, "legacy", None, None)

    monkeypatch.setattr(bioactivity, "_read_json", fail)
    fallback = bioactivity._assay_metadata("CHEMBL2", "Feed assay", "F", cache)
    assert fallback.confidence_score == 0
    assert fallback.description == "Feed assay"


def test_activity_rows_guard_snapshot_page_size(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject activity feeds that exceed the deterministic one-page snapshot boundary."""

    monkeypatch.setattr(
        bioactivity,
        "_read_json",
        lambda _url: {"page_meta": {"next": None}, "activities": [{"activity_id": 1}]},
    )
    assert bioactivity._activity_rows() == [{"activity_id": 1}]
    monkeypatch.setattr(
        bioactivity,
        "_read_json",
        lambda _url: {"page_meta": {"next": "next-page"}, "activities": []},
    )
    with pytest.raises(ValueError, match="page size"):
        bioactivity._activity_rows()


def test_drug_document_rejects_unknown_references() -> None:
    """Keep every exported cross-reference resolvable inside the public document."""

    base = drug_document()
    mutations = [
        lambda document: document["generations"][0]["drug_ids"].append("ghost-drug"),
        lambda document: document["target_links"][0].update({"drug_id": "ghost-drug"}),
        lambda document: document["resistance_mutations"][0].update({"site_id": "ghost-site"}),
        lambda document: document["bioactivity"][0].update({"drug_id": "ghost-drug"}),
        lambda document: document["bioactivity"][0]["activities"][0].update(
            {"target_chembl_id": "CHEMBL999999"}
        ),
    ]
    for mutate in mutations:
        document = deepcopy(base)
        mutate(document)
        with pytest.raises(ValidationError):
            DrugDocument.model_validate(document)


def test_validator_main_reports_metrics(capsys: pytest.CaptureFixture[str]) -> None:
    """Expose Phase 5 release metrics through the command-line entry point."""

    assert validate_main() == 0
    assert "bioactivity_label_count: 275" in capsys.readouterr().out


def test_bioactivity_main_reports_refresh_counts(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Expose refresh metrics through the command-line entry point."""

    compounds = load_bioactivity_snapshot()[:1]
    monkeypatch.setattr(bioactivity, "refresh_bioactivity_snapshot", lambda _path: compounds)
    monkeypatch.setattr(sys, "argv", ["bioactivity", "--output", "unused.json"])
    assert bioactivity.main() == 0
    assert "refreshed 1 compounds" in capsys.readouterr().out


def test_graph_writer_includes_drug_layer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Generate the Phase 5 drug exchange artifact with the graph bundle."""

    monkeypatch.setattr("mtor_nexus.graph.web_exports.write_web_exports", lambda *_args: None)
    builder = MTORGraphBuilder()
    builder.build()
    builder.write_all(str(tmp_path / "processed"))
    assert (tmp_path / "processed" / "drug-layer.json").exists()


def test_release_validator_clis(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Run the graph and disease validator command-line entry points."""

    monkeypatch.setattr(sys, "argv", ["graph-validate"])
    assert graph_validate_main() == 0
    monkeypatch.setattr(sys, "argv", ["disease-validate"])
    assert disease_validate_main() == 0
    output = capsys.readouterr().out
    assert "node_count: 263" in output
    assert "disease_class_count: 8" in output


def test_source_index_cli_includes_chembl(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Write the source index with its ChEMBL handling and drug-layer entry."""

    output = tmp_path / "source-index.json"
    monkeypatch.setattr(sys, "argv", ["source-index", "--output", str(output)])
    assert source_index_main() == 0
    index = json.loads(output.read_text(encoding="utf-8"))
    assert (
        index["sources"]["chembl"]["handling"]
        == "rdkit-standardized-bioactivity-counter-screen-snapshot"
    )
    assert index["derived_artifacts"]["drug_layer"]["path"] == "data/processed/drug-layer.json"
    assert "indexed 12 pinned source(s)" in capsys.readouterr().out


def test_binding_mode_viewer_contains_site_and_resistance_labels() -> None:
    """Keep the Mol* binding-mode UI and its resistance labels visible."""

    viewer = Path("webapp/components/drug/BindingModeViewer.tsx").read_text(encoding="utf-8")
    assert "Mol* binding-mode viewer" in viewer
    assert "bisteric_frb_atp" in viewer
    assert "Resistance annotation" in viewer
