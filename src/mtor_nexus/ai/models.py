"""Typed contracts for the Phase 6 AI triage engine."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from mtor_nexus.drugs.models import BindingMode
from mtor_nexus.schema import SpeciesEvidence, Tier


class AIReleaseStatus(StrEnum):
    """Measured release state for an AI component."""

    BLOCKED = "blocked"
    VALIDATED = "validated"


class PredictionStatus(StrEnum):
    """Whether an engine returned a prediction or an explicit refusal."""

    REFUSED = "refused"
    PREPARED = "prepared"
    PREDICTED = "predicted"


class RefusalReason(StrEnum):
    """Reasons an AI surface must decline to emit a numerical prediction."""

    INVALID_SMILES = "invalid_smiles"
    OUT_OF_APPLICABILITY_DOMAIN = "out_of_applicability_domain"
    MODEL_NOT_VALIDATED = "model_not_validated"
    COFOLDING_NOT_CONFIGURED = "cofolding_not_configured"


class TargetDataAudit(BaseModel):
    """Observed ChEMBL training density for one selectivity task."""

    model_config = ConfigDict(extra="forbid")

    target: str = Field(min_length=1)
    compound_count: int = Field(ge=0)
    label_count: int = Field(ge=0)
    minimum_compounds: int = Field(gt=0)
    ready: bool


class SelectivityArchitecture(BaseModel):
    """Pre-registered D-MPNN training architecture."""

    model_config = ConfigDict(extra="forbid")

    encoder: str
    hidden_size: int
    depth: int
    ensemble_size: int
    dropout: float
    targets: list[str]
    pocket_descriptor: str
    uncertainty: str
    calibration: str
    applicability_domain: str


class LockedAcceptanceCriteria(BaseModel):
    """Pre-registered model gates that cannot be inferred or waived."""

    model_config = ConfigDict(extra="forbid")

    target_r2_minimums: dict[str, float]
    selectivity_auroc_minimum: float
    conformal_coverage_minimum: float
    conformal_coverage_maximum: float
    torin2_benchmark_required: bool
    deterministic_weights_required: bool
    a100_no_oom_required: bool


class SelectivityReleaseReport(BaseModel):
    """Measured readiness report for the selectivity centerpiece."""

    model_config = ConfigDict(extra="forbid")

    release_status: AIReleaseStatus
    blocking_reasons: list[str]
    training_snapshot: str
    training_compound_count: int = Field(ge=0)
    training_label_count: int = Field(ge=0)
    target_audit: list[TargetDataAudit]
    klifs_descriptors_loaded: bool
    validated_model_artifact_loaded: bool
    a100_no_oom_tested: bool
    target_r2: dict[str, float | None]
    selectivity_auroc: float | None
    conformal_coverage: dict[str, float | None]
    torin2_benchmark_passed: bool | None
    deterministic_weights_passed: bool | None
    locked_acceptance: LockedAcceptanceCriteria


class ApplicabilityDomainResult(BaseModel):
    """Nearest-neighbor Morgan-fingerprint applicability assessment."""

    model_config = ConfigDict(extra="forbid")

    in_domain: bool
    nearest_similarity: float = Field(ge=0, le=1)
    nearest_drug_id: str | None
    threshold: float = Field(ge=0, le=1)


class TargetPrediction(BaseModel):
    """One calibrated target-level pIC50 prediction."""

    model_config = ConfigDict(extra="forbid")

    target: str
    pic50: float
    conformal_low: float
    conformal_high: float


class SelectivityPrediction(BaseModel):
    """Serving response for the mTOR-vs-PIKK/PI3K predictor."""

    model_config = ConfigDict(extra="forbid")

    status: PredictionStatus
    standardized_smiles: str | None
    applicability_domain: ApplicabilityDomainResult | None
    refusal_reason: RefusalReason | None
    message: str
    per_target_pic50: list[TargetPrediction] = Field(default_factory=list[TargetPrediction])
    selectivity_margin: float | None = None
    classification: str | None = None
    calibrated_confidence: float | None = None


class CofoldingTriageResult(BaseModel):
    """Boltz-2 handoff result with mandatory experimental-validation policy."""

    model_config = ConfigDict(extra="forbid")

    status: PredictionStatus
    standardized_smiles: str | None
    receptor: str
    refusal_reason: RefusalReason
    message: str
    boltz_yaml_template: str | None
    predicted_affinity: float | None = None
    pose_confidence: float | None = None
    required_experimental_validation: bool = True


class ResistanceLiability(BaseModel):
    """Computational resistance liability attached to a binding mode."""

    model_config = ConfigDict(extra="forbid")

    mutation_id: str
    domain: str
    effect: str
    tier: Tier = Tier.SPECULATIVE
    species_evidence: list[SpeciesEvidence] = Field(
        default_factory=lambda: [SpeciesEvidence.COMPUTATIONAL]
    )
    required_experimental_validation: bool = True


class CombinationSuggestion(BaseModel):
    """Graph-grounded combination hypothesis."""

    model_config = ConfigDict(extra="forbid")

    partner: str
    rationale: str
    tier: Tier = Tier.SPECULATIVE
    species_evidence: list[SpeciesEvidence] = Field(
        default_factory=lambda: [SpeciesEvidence.COMPUTATIONAL]
    )
    required_experimental_validation: bool = True


class ResistancePrediction(BaseModel):
    """Resistance and combination triage result."""

    model_config = ConfigDict(extra="forbid")

    binding_mode: BindingMode
    liabilities: list[ResistanceLiability]
    combinations: list[CombinationSuggestion]
    required_experimental_validation: bool = True


class ScaffoldCandidate(BaseModel):
    """Computational-only scaffold suggestion."""

    model_config = ConfigDict(extra="forbid")

    scaffold_id: str
    smiles: str
    synthetic_accessibility_proxy: float = Field(ge=1, le=10)
    admet_filter_passed: bool
    admet_notes: list[str]
    selectivity: SelectivityPrediction
    tier: Tier = Tier.SPECULATIVE
    species_evidence: list[SpeciesEvidence] = Field(
        default_factory=lambda: [SpeciesEvidence.COMPUTATIONAL]
    )
    tag: str = "red_computational_only_unvalidated"
    required_experimental_validation: bool = True


class PredictionRequest(BaseModel):
    """User request accepted by the prediction API."""

    model_config = ConfigDict(extra="forbid")

    smiles: str = Field(min_length=1)
    binding_mode: BindingMode = BindingMode.ATP_COMPETITIVE
    include_cofolding: bool = False


class PredictionBundle(BaseModel):
    """Combined honest prediction response returned by the API."""

    model_config = ConfigDict(extra="forbid")

    selectivity: SelectivityPrediction
    resistance: ResistancePrediction
    cofolding: CofoldingTriageResult | None = None


class Phase6PrereleaseReport(BaseModel):
    """Measured acceptance report for the refusal-bound Phase 6 prerelease."""

    model_config = ConfigDict(extra="forbid")

    scientific_release_ready: bool
    selectivity_release_status: AIReleaseStatus
    training_compound_count: int = Field(ge=0)
    training_label_count: int = Field(ge=0)
    refusal_checks_passed: bool
    cofolding_handoff_check_passed: bool
    resistance_triage_check_passed: bool
    scaffold_policy_check_passed: bool
    documentation_check_passed: bool
    blocking_reasons: list[str]
