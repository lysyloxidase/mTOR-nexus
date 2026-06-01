"""Validate the Phase 4 disease and mutation overlay."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mtor_nexus.disease.classes import CBIOPORTAL_ER_POSITIVE_PIK3CA, DISEASE_CLASSES
from mtor_nexus.disease.cosmic_overlay import load_cosmic_overlay
from mtor_nexus.disease.export import disease_document, write_disease_exports
from mtor_nexus.disease.live_probe import probe_cbioportal_pik3ca_er_positive, probe_clinvar
from mtor_nexus.disease.models import FunctionalEffect, MutationRecord, MutationSource
from mtor_nexus.disease.mutations import curated_mutations
from mtor_nexus.disease.validate import REQUIRED_MUTATION_GENES, validate_phase4_layer
from mtor_nexus.schema import SpeciesEvidence, Tier


def test_phase4_release_metrics() -> None:
    """Protect disease-class, association, mutation, and syndrome coverage."""

    report = validate_phase4_layer()
    assert report.disease_class_count == 8
    assert report.association_count >= 8
    assert report.mutation_count >= 12
    assert report.mutation_gene_count >= len(REQUIRED_MUTATION_GENES)
    assert report.rare_syndrome_count == 6


def test_required_signature_mutations_and_species_caveats() -> None:
    """Keep required human genetics and rodent translation caveats visible."""

    genes = {mutation.gene_symbol for mutation in curated_mutations()}
    assert genes >= REQUIRED_MUTATION_GENES
    assert DISEASE_CLASSES["aging_longevity"].species_caveat
    assert DISEASE_CLASSES["metabolic"].species_caveat
    assert CBIOPORTAL_ER_POSITIVE_PIK3CA.frequency_percent == pytest.approx(33.54, abs=0.01)


def test_mutation_schema_rejects_malformed_hgvs() -> None:
    """Reject mutation nodes that cannot be reconciled by HGVS."""

    with pytest.raises(ValidationError):
        MutationRecord(
            mutation_id="MUT:BAD",
            gene_symbol="MTOR",
            hgvs_protein="E1799K",
            hgvs_coding="5395G>A",
            functional_effect=FunctionalEffect.ACTIVATING,
            tier=Tier.ROBUST,
            species_evidence=[SpeciesEvidence.HUMAN],
            sources=[MutationSource.CLINVAR],
            source_refs=["clinvar:VCV000217823.74"],
        )


def test_disease_export_is_browser_ready(tmp_path: Path) -> None:
    """Write identical normalized and browser-facing disease documents."""

    processed = tmp_path / "processed.json"
    web = tmp_path / "web.json"
    write_disease_exports(str(processed), str(web))
    document = disease_document()
    assert json.loads(processed.read_text(encoding="utf-8")) == document
    assert json.loads(web.read_text(encoding="utf-8")) == document
    assert not document["metadata"]["cosmic_raw_redistributed"]


def test_cosmic_overlay_loads_only_curator_provided_snapshot(tmp_path: Path) -> None:
    """Load the minimal licensed COSMIC reconciliation format locally."""

    overlay = tmp_path / "cosmic.tsv"
    overlay.write_text(
        "COSMIC_ID\tGENE_SYMBOL\tHGVSP\nCOSM763\tPIK3CA\tp.Glu545Lys\n",
        encoding="utf-8",
    )
    records = load_cosmic_overlay(str(overlay))
    assert records[0].cosmic_id == "COSM763"
    assert records[0].gene_symbol == "PIK3CA"


def test_live_disease_probe_parsers_without_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Calculate cBioPortal and ClinVar probe summaries without live endpoints."""

    def fake_read_json(url: str) -> object:
        if "mutations" in url:
            return [{"patientId": "P1"}, {"patientId": "P3"}]
        if "clinical-data" in url:
            return [
                {"patientId": "P1", "clinicalAttributeId": "ER_STATUS_BY_IHC", "value": "Positive"},
                {"patientId": "P2", "clinicalAttributeId": "ER_STATUS_BY_IHC", "value": "Positive"},
            ]
        return {"esearchresult": {"count": "1", "idlist": ["217823"]}}

    monkeypatch.setattr("mtor_nexus.disease.live_probe._read_json", fake_read_json)
    cbioportal = probe_cbioportal_pik3ca_er_positive()
    assert cbioportal.altered_patients == 1
    assert cbioportal.frequency_percent == 50
    assert probe_clinvar().first_variation_id == "217823"


def test_committed_disease_export_matches_public_overlay() -> None:
    """Keep committed analysis and browser overlays byte-for-byte aligned."""

    processed = Path("data/processed/disease-layer.json").read_text(encoding="utf-8")
    public = Path("webapp/public/data/diseases.json").read_text(encoding="utf-8")
    assert processed == public
