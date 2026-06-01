"""Refusal-bound serving shell and readiness audit for the selectivity GNN.

No numerical predictor is shipped until a trained artifact satisfies the
pre-registered acceptance criteria. The module still provides the production
applicability-domain gate and a machine-readable D-MPNN training contract.
"""

from collections import Counter, defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator

from mtor_nexus.ai.models import (
    AIReleaseStatus,
    ApplicabilityDomainResult,
    LockedAcceptanceCriteria,
    PredictionStatus,
    RefusalReason,
    SelectivityArchitecture,
    SelectivityPrediction,
    SelectivityReleaseReport,
    TargetDataAudit,
)
from mtor_nexus.drugs.bioactivity import load_bioactivity_snapshot, standardize_smiles

TARGETS = ["MTOR", "PIK3CA", "ATM", "ATR", "PRKDC"]
MINIMUM_COMPOUNDS_PER_TARGET = 30
APPLICABILITY_THRESHOLD = 0.3
KLIFS_DESCRIPTOR_PATH = "data/curated/klifs-pocket-descriptors.json"
VALIDATED_ARTIFACT_PATH = "data/models/selectivity-gnn-validated.json"
_mol_from_smiles = cast(Callable[[str], Any], Chem.MolFromSmiles)  # pyright: ignore[reportUnknownMemberType]
_tanimoto = cast(Callable[[Any, Any], float], DataStructs.TanimotoSimilarity)
_morgan_generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
_fingerprint = cast(Callable[[Any], Any], _morgan_generator.GetFingerprint)  # pyright: ignore[reportUnknownMemberType]


def locked_acceptance_criteria() -> LockedAcceptanceCriteria:
    """Return immutable scientific acceptance gates for a future training run."""

    return LockedAcceptanceCriteria(
        target_r2_minimums={"MTOR": 0.60, "PIK3CA": 0.55, "ATM": 0.50, "ATR": 0.50, "PRKDC": 0.50},
        selectivity_auroc_minimum=0.80,
        conformal_coverage_minimum=0.88,
        conformal_coverage_maximum=0.92,
        torin2_benchmark_required=True,
        deterministic_weights_required=True,
        a100_no_oom_required=True,
    )


def architecture_contract() -> SelectivityArchitecture:
    """Describe the pre-registered Chemprop-style training architecture."""

    return SelectivityArchitecture(
        encoder="directed_message_passing_neural_network",
        hidden_size=300,
        depth=5,
        ensemble_size=5,
        dropout=0.2,
        targets=TARGETS,
        pocket_descriptor="KLIFS 85-residue aligned pocket descriptor, frozen per target",
        uncertainty="deep ensemble plus Monte-Carlo dropout",
        calibration="temperature scaling plus split conformal prediction",
        applicability_domain="Morgan radius=2, 2048-bit Tanimoto nearest-neighbor threshold >= 0.3",
    )


class ApplicabilityDomainGate:
    """Refuse molecules outside the observed training chemical space."""

    def __init__(self, threshold: float = APPLICABILITY_THRESHOLD) -> None:
        """Build Morgan fingerprints from the committed Phase 5 snapshot."""

        self.threshold = threshold
        self._training: list[tuple[str, Any]] = []
        for compound in load_bioactivity_snapshot():
            molecule = _mol_from_smiles(compound.rdkit_standardized_smiles)
            if molecule is None:
                raise ValueError(f"training snapshot contains invalid SMILES: {compound.drug_id}")
            self._training.append((compound.drug_id, _fingerprint(molecule)))

    def evaluate(self, query_smiles: str) -> ApplicabilityDomainResult:
        """Return the nearest training neighbor and threshold decision."""

        standardized = standardize_smiles(query_smiles)
        molecule = _mol_from_smiles(standardized)
        if molecule is None:
            raise ValueError("RDKit could not parse standardized query SMILES")
        fingerprint = _fingerprint(molecule)
        neighbor, similarity = max(
            (
                (drug_id, _tanimoto(fingerprint, training_fp))
                for drug_id, training_fp in self._training
            ),
            key=lambda item: item[1],
        )
        return ApplicabilityDomainResult(
            in_domain=similarity >= self.threshold,
            nearest_similarity=similarity,
            nearest_drug_id=neighbor,
            threshold=self.threshold,
        )

    def check(self, query_smiles: str) -> tuple[bool, float]:
        """Return the compact tuple interface used by training workflows."""

        result = self.evaluate(query_smiles)
        return result.in_domain, result.nearest_similarity


def training_data_audit() -> SelectivityReleaseReport:
    """Audit whether the committed snapshot can support model acceptance tests."""

    compounds = load_bioactivity_snapshot()
    rows = [row for compound in compounds for row in compound.activities]
    label_counts = Counter(row.target_gene_symbol for row in rows)
    compound_ids: defaultdict[str, set[str]] = defaultdict(set)
    for row in rows:
        compound_ids[row.target_gene_symbol].add(row.drug_id)
    target_audit = [
        TargetDataAudit(
            target=target,
            compound_count=len(compound_ids[target]),
            label_count=label_counts[target],
            minimum_compounds=MINIMUM_COMPOUNDS_PER_TARGET,
            ready=len(compound_ids[target]) >= MINIMUM_COMPOUNDS_PER_TARGET,
        )
        for target in TARGETS
    ]
    klifs_loaded = Path(KLIFS_DESCRIPTOR_PATH).exists()
    artifact_loaded = Path(VALIDATED_ARTIFACT_PATH).exists()
    reasons: list[str] = []
    sparse_targets = [target for target in target_audit if not target.ready]
    if sparse_targets:
        reasons.append(
            "counter-screen training data are too sparse for locked train/validation/test gates: "
            + ", ".join(f"{target.target}={target.compound_count}" for target in sparse_targets)
        )
    if not klifs_loaded:
        reasons.append("KLIFS pocket descriptors have not been ingested")
    if not artifact_loaded:
        reasons.append("no validated selectivity-GNN artifact is present")
    reasons.append("1x A100 no-OOM training gate has not been executed in this environment")
    return SelectivityReleaseReport(
        release_status=AIReleaseStatus.BLOCKED,
        blocking_reasons=reasons,
        training_snapshot="data/curated/chembl-bioactivity.json",
        training_compound_count=len(compounds),
        training_label_count=len(rows),
        target_audit=target_audit,
        klifs_descriptors_loaded=klifs_loaded,
        validated_model_artifact_loaded=artifact_loaded,
        a100_no_oom_tested=False,
        target_r2={target: None for target in TARGETS},
        selectivity_auroc=None,
        conformal_coverage={target: None for target in TARGETS},
        torin2_benchmark_passed=None,
        deterministic_weights_passed=None,
        locked_acceptance=locked_acceptance_criteria(),
    )


class SelectivityGNN:
    """Serving shell that refuses until a measured, validated artifact exists."""

    def __init__(self, gate: ApplicabilityDomainGate | None = None) -> None:
        """Load the production applicability gate and current release report."""

        self.gate = gate or ApplicabilityDomainGate()
        self.release_report = training_data_audit()

    def predict(self, smiles: str) -> SelectivityPrediction:
        """Assess domain membership and refuse unsupported numerical inference."""

        try:
            standardized = standardize_smiles(smiles)
            domain = self.gate.evaluate(standardized)
        except ValueError:
            return SelectivityPrediction(
                status=PredictionStatus.REFUSED,
                standardized_smiles=None,
                applicability_domain=None,
                refusal_reason=RefusalReason.INVALID_SMILES,
                message="invalid SMILES - RDKit could not parse the query",
            )
        if not domain.in_domain:
            return SelectivityPrediction(
                status=PredictionStatus.REFUSED,
                standardized_smiles=standardized,
                applicability_domain=domain,
                refusal_reason=RefusalReason.OUT_OF_APPLICABILITY_DOMAIN,
                message="out-of-applicability-domain - prediction unreliable",
            )
        return SelectivityPrediction(
            status=PredictionStatus.REFUSED,
            standardized_smiles=standardized,
            applicability_domain=domain,
            refusal_reason=RefusalReason.MODEL_NOT_VALIDATED,
            message=(
                "selectivity model is not validated - numerical pIC50 values are withheld "
                "until the locked scientific acceptance gates pass"
            ),
        )
