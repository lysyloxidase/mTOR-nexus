"""Validate the Phase 6 refusal-bound AI triage prerelease."""

import json
import sys
from pathlib import Path

import pytest

from mtor_nexus.ai import AIEngine, generative, selectivity_gnn
from mtor_nexus.ai.cofolding import CofoldingTriage
from mtor_nexus.ai.export import write_ai_exports
from mtor_nexus.ai.generative import ScaffoldExplorer
from mtor_nexus.ai.models import (
    AIReleaseStatus,
    PredictionRequest,
    PredictionStatus,
    RefusalReason,
)
from mtor_nexus.ai.resistance import ResistancePredictor
from mtor_nexus.ai.selectivity_gnn import (
    APPLICABILITY_THRESHOLD,
    ApplicabilityDomainGate,
    SelectivityGNN,
    architecture_contract,
    locked_acceptance_criteria,
    training_data_audit,
)
from mtor_nexus.ai.service import ai_status_document
from mtor_nexus.ai.validate import main as validate_main
from mtor_nexus.ai.validate import validate_phase6_prerelease
from mtor_nexus.drugs.bioactivity import load_bioactivity_snapshot
from mtor_nexus.drugs.models import BindingMode


def test_selectivity_contract_and_sparse_readiness_audit() -> None:
    """Keep the registered architecture and measured blockers explicit."""

    architecture = architecture_contract()
    audit = training_data_audit()
    assert architecture.encoder == "directed_message_passing_neural_network"
    assert architecture.targets == ["MTOR", "PIK3CA", "ATM", "ATR", "PRKDC"]
    assert architecture.hidden_size == 300
    assert architecture.depth == 5
    assert architecture.ensemble_size == 5
    assert locked_acceptance_criteria().selectivity_auroc_minimum == 0.80
    assert audit.release_status == AIReleaseStatus.BLOCKED
    assert audit.training_compound_count == 23
    assert audit.training_label_count == 275
    assert {row.target: row.compound_count for row in audit.target_audit} == {
        "MTOR": 16,
        "PIK3CA": 11,
        "ATM": 2,
        "ATR": 7,
        "PRKDC": 7,
    }
    assert audit.target_r2["MTOR"] is None
    assert audit.torin2_benchmark_passed is None


def test_audit_detects_present_descriptor_and_artifact_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exercise the file-presence audit without treating files as measured gates."""

    descriptors = tmp_path / "klifs.json"
    artifact = tmp_path / "artifact.json"
    descriptors.write_text("{}\n", encoding="utf-8")
    artifact.write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(selectivity_gnn, "KLIFS_DESCRIPTOR_PATH", str(descriptors))
    monkeypatch.setattr(selectivity_gnn, "VALIDATED_ARTIFACT_PATH", str(artifact))
    audit = training_data_audit()
    assert audit.klifs_descriptors_loaded
    assert audit.validated_model_artifact_loaded
    assert not any("KLIFS" in reason for reason in audit.blocking_reasons)
    assert not any("no validated" in reason for reason in audit.blocking_reasons)


def test_applicability_gate_and_selectivity_shell_refuse_unsupported_output() -> None:
    """Refuse invalid, out-of-domain, and unvalidated in-domain queries."""

    known = load_bioactivity_snapshot()[0].rdkit_standardized_smiles
    gate = ApplicabilityDomainGate()
    exact = gate.evaluate(known)
    assert gate.check(known) == (True, 1.0)
    assert exact.nearest_similarity == 1.0
    assert exact.threshold == APPLICABILITY_THRESHOLD
    with pytest.raises(ValueError, match="RDKit"):
        gate.evaluate("not-smiles")

    shell = SelectivityGNN(gate)
    invalid = shell.predict("not-smiles")
    assert invalid.refusal_reason == RefusalReason.INVALID_SMILES
    out_of_domain = shell.predict("C")
    assert out_of_domain.refusal_reason == RefusalReason.OUT_OF_APPLICABILITY_DOMAIN
    assert out_of_domain.message == "out-of-applicability-domain - prediction unreliable"
    in_domain = shell.predict(known)
    assert in_domain.refusal_reason == RefusalReason.MODEL_NOT_VALIDATED
    assert in_domain.status == PredictionStatus.REFUSED
    assert not in_domain.per_target_pic50


def test_cofolding_handoff_prepares_yaml_and_refuses_invalid_smiles() -> None:
    """Prepare reviewed-sequence YAML without pretending to run Boltz-2."""

    handoff = CofoldingTriage()
    prepared = handoff.prepare("CC")
    assert prepared.status == PredictionStatus.PREPARED
    assert "PASTE_REVIEWED_HUMAN_MTOR_CONSTRUCT_SEQUENCE_HERE" in (
        prepared.boltz_yaml_template or ""
    )
    assert prepared.predicted_affinity is None
    assert prepared.required_experimental_validation
    invalid = handoff.prepare("not-smiles")
    assert invalid.status == PredictionStatus.REFUSED
    assert invalid.refusal_reason == RefusalReason.INVALID_SMILES
    assert invalid.boltz_yaml_template is None


@pytest.mark.parametrize(
    ("binding_mode", "expected"),
    [
        (BindingMode.FRB_ALLOSTERIC, {"A2034V", "F2108L"}),
        (BindingMode.ATP_COMPETITIVE, {"M2327I"}),
        (BindingMode.DUAL_PI3K_MTOR_ATP, {"M2327I"}),
        (BindingMode.BISTERIC_FRB_ATP, {"A2034V", "F2108L", "M2327I"}),
        (BindingMode.RICTOR_MTOR_ASSOCIATION, set()),
    ],
)
def test_resistance_predictor_maps_binding_mode_liabilities(
    binding_mode: BindingMode, expected: set[str]
) -> None:
    """Attach only structural liabilities relevant to the selected mode."""

    prediction = ResistancePredictor().predict(binding_mode)
    assert {liability.mutation_id for liability in prediction.liabilities} == expected
    assert bool(prediction.combinations) == (binding_mode == BindingMode.FRB_ALLOSTERIC)
    assert prediction.required_experimental_validation


def test_scaffold_explorer_marks_all_candidates_as_unvalidated() -> None:
    """Keep deterministic scaffold hypotheses red-tagged and refusal-bound."""

    explorer = ScaffoldExplorer()
    assert explorer.generate(-1) == []
    candidates = explorer.generate(2)
    assert len(candidates) == 2
    assert all(candidate.tag == "red_computational_only_unvalidated" for candidate in candidates)
    assert all(candidate.required_experimental_validation for candidate in candidates)
    assert all(candidate.admet_notes[-1].startswith("heuristic filter") for candidate in candidates)
    assert all(candidate.selectivity.status == PredictionStatus.REFUSED for candidate in candidates)
    with pytest.raises(ValueError, match="internal scaffold"):
        generative._developability("not-smiles")


def test_engine_status_export_and_prediction_bundle(tmp_path: Path) -> None:
    """Serve and export the same explicit prerelease boundary."""

    engine = AIEngine()
    result = engine.predict(
        PredictionRequest(
            smiles="CC",
            binding_mode=BindingMode.FRB_ALLOSTERIC,
            include_cofolding=True,
        )
    )
    assert result.selectivity.status == PredictionStatus.REFUSED
    assert result.cofolding is not None
    assert engine.predict(PredictionRequest(smiles="CC")).cofolding is None
    assert len(engine.generate_scaffolds(1)) == 1
    status = ai_status_document()
    assert status["scientific_release_ready"] is False
    assert status["selectivity_gnn"]["release_status"] == "blocked"

    processed = tmp_path / "processed.json"
    web = tmp_path / "web.json"
    write_ai_exports(str(processed), str(web))
    assert json.loads(processed.read_text(encoding="utf-8")) == json.loads(
        web.read_text(encoding="utf-8")
    )


def test_phase6_validator_writes_machine_readable_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Commit a report that distinguishes prerelease validation from model release."""

    report = validate_phase6_prerelease()
    assert report.refusal_checks_passed
    assert not report.scientific_release_ready
    output = tmp_path / "ai-validation.json"
    monkeypatch.setattr(sys, "argv", ["ai-validate", "--output", str(output)])
    assert validate_main() == 0
    assert json.loads(output.read_text(encoding="utf-8"))["scientific_release_ready"] is False
