"""Validate the honest Phase 6 prerelease boundary."""

import argparse
from pathlib import Path

from mtor_nexus.ai.cofolding import CofoldingTriage
from mtor_nexus.ai.generative import ScaffoldExplorer
from mtor_nexus.ai.models import (
    AIReleaseStatus,
    Phase6PrereleaseReport,
    PredictionStatus,
    RefusalReason,
)
from mtor_nexus.ai.resistance import ResistancePredictor
from mtor_nexus.ai.selectivity_gnn import SelectivityGNN, training_data_audit
from mtor_nexus.drugs.bioactivity import load_bioactivity_snapshot
from mtor_nexus.drugs.models import BindingMode

MODEL_CARD_PATH = "docs/ai-model-cards.md"


def _documentation_is_complete(path: str = MODEL_CARD_PATH) -> bool:
    """Require named cards and the prerelease refusal policy."""

    content = Path(path).read_text(encoding="utf-8")
    required_sections = [
        "## Selectivity GNN",
        "## Boltz-2 Cofolding Handoff",
        "## Resistance Triage",
        "## Scaffold Explorer",
        "## Locked Scientific Gates",
        "out-of-applicability-domain",
        "Research use only",
    ]
    return all(section in content for section in required_sections)


def validate_phase6_prerelease() -> Phase6PrereleaseReport:
    """Exercise refusal, handoff, liability, scaffold, and documentation policies."""

    audit = training_data_audit()
    assert audit.release_status == AIReleaseStatus.BLOCKED
    assert audit.torin2_benchmark_passed is None
    assert audit.selectivity_auroc is None
    assert any(not target.ready for target in audit.target_audit)

    shell = SelectivityGNN()
    invalid = shell.predict("not-smiles")
    assert invalid.refusal_reason == RefusalReason.INVALID_SMILES
    assert not invalid.per_target_pic50
    out_of_domain = shell.predict("C")
    assert out_of_domain.refusal_reason == RefusalReason.OUT_OF_APPLICABILITY_DOMAIN
    assert out_of_domain.applicability_domain is not None
    assert not out_of_domain.applicability_domain.in_domain
    known_smiles = load_bioactivity_snapshot()[0].rdkit_standardized_smiles
    in_domain = shell.predict(known_smiles)
    assert in_domain.refusal_reason == RefusalReason.MODEL_NOT_VALIDATED
    assert in_domain.applicability_domain is not None
    assert in_domain.applicability_domain.in_domain
    assert not in_domain.per_target_pic50

    cofolding = CofoldingTriage().prepare(known_smiles)
    assert cofolding.status == PredictionStatus.PREPARED
    assert cofolding.predicted_affinity is None
    assert cofolding.pose_confidence is None
    assert cofolding.required_experimental_validation
    assert cofolding.boltz_yaml_template is not None

    resistance = ResistancePredictor().predict(BindingMode.FRB_ALLOSTERIC)
    assert {liability.mutation_id for liability in resistance.liabilities} == {
        "A2034V",
        "F2108L",
    }
    assert resistance.combinations[0].partner == "AKT inhibitor"
    assert resistance.required_experimental_validation

    scaffolds = ScaffoldExplorer(shell).generate()
    assert len(scaffolds) == 3
    assert all(candidate.tag == "red_computational_only_unvalidated" for candidate in scaffolds)
    assert all(candidate.required_experimental_validation for candidate in scaffolds)
    assert all(candidate.selectivity.status == PredictionStatus.REFUSED for candidate in scaffolds)

    report = Phase6PrereleaseReport(
        scientific_release_ready=False,
        selectivity_release_status=audit.release_status,
        training_compound_count=audit.training_compound_count,
        training_label_count=audit.training_label_count,
        refusal_checks_passed=True,
        cofolding_handoff_check_passed=True,
        resistance_triage_check_passed=True,
        scaffold_policy_check_passed=True,
        documentation_check_passed=_documentation_is_complete(),
        blocking_reasons=audit.blocking_reasons,
    )
    assert report.documentation_check_passed
    return report


def main() -> int:
    """Write a machine-readable prerelease-validation report."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/processed/ai-validation.json")
    args = parser.parse_args()
    report = validate_phase6_prerelease()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(
        "validated Phase 6 prerelease refusal policy; "
        "scientific selectivity-model release remains blocked"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
