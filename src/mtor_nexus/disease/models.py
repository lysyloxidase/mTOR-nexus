"""Typed disease, mutation, and pathway-association models."""

import re
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mtor_nexus.schema import SpeciesEvidence, Tier

HGVS_CODING_PATTERN = re.compile(r"^c\.\d+(?:[+-]\d+)?(?:[ACGT]>[ACGT]|del|dup|ins[ACGT]+)$")
HGVS_PROTEIN_PATTERN = re.compile(r"^p\.(?:[A-Z][a-z]{2}\d+(?:[A-Z][a-z]{2}|Ter|fs)|\?)$")


class PerturbationDirection(StrEnum):
    """Direction in which a disease association perturbs pathway activity."""

    HYPERACTIVATION = "hyperactivation"
    LOSS = "loss"
    MIXED = "mixed"
    UNCERTAIN = "uncertain"


class FunctionalEffect(StrEnum):
    """Functional interpretation attached to a genetic alteration."""

    ACTIVATING = "activating"
    LOSS_OF_FUNCTION = "loss_of_function"
    UNKNOWN = "unknown"


class MutationSource(StrEnum):
    """Mutation-source surfaces represented by the disease layer."""

    CLINVAR = "clinvar"
    CBIOPORTAL = "cbioportal"
    CURATED = "curated"


class ApprovedDrug(BaseModel):
    """Approved or clinically used disease-linked mTOR intervention."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    indication: str = Field(min_length=1)
    status: str = Field(min_length=1)
    source_url: str = Field(min_length=1)


class TrialLink(BaseModel):
    """ClinicalTrials.gov study reference."""

    model_config = ConfigDict(extra="forbid")

    nct_id: str = Field(pattern=r"^NCT\d{8}$")
    title: str = Field(min_length=1)
    url: str = Field(min_length=1)


class RareSyndrome(BaseModel):
    """Rare syndrome detail presented by the disease UI."""

    model_config = ConfigDict(extra="forbid")

    syndrome_id: str = Field(min_length=1)
    genes: list[str] = Field(min_length=1)
    drug: str | None = None
    inheritance: str | None = None
    recurrent_variant: str | None = None
    omim: str | None = None


class CohortFrequency(BaseModel):
    """Derived cBioPortal frequency with an explicit cohort denominator."""

    model_config = ConfigDict(extra="forbid")

    gene_symbol: str = Field(min_length=1)
    cohort: str = Field(min_length=1)
    altered_cases: int = Field(ge=0)
    profiled_cases: int = Field(gt=0)
    frequency_percent: float = Field(ge=0, le=100)
    source_url: str = Field(min_length=1)

    @model_validator(mode="after")
    def frequency_matches_counts(self) -> "CohortFrequency":
        """Keep committed derived frequencies consistent with their denominators."""

        expected = self.altered_cases * 100 / self.profiled_cases
        if abs(self.frequency_percent - expected) > 0.01:
            raise ValueError("frequency percent must match altered/profiled counts")
        return self


class DiseaseClass(BaseModel):
    """One evidence-tagged disease overlay."""

    model_config = ConfigDict(extra="forbid")

    disease_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    key_nodes: list[str] = Field(min_length=1)
    tier: Tier
    species_evidence: list[SpeciesEvidence] = Field(min_length=1)
    mechanism: str = Field(min_length=1)
    diseases: list[str] = Field(default_factory=list)
    indications: list[str] = Field(default_factory=list)
    species_caveat: str | None = None
    approved_drugs: list[ApprovedDrug] = Field(default_factory=list[ApprovedDrug])
    trial_links: list[TrialLink] = Field(default_factory=list[TrialLink])
    rare_syndromes: list[RareSyndrome] = Field(default_factory=list[RareSyndrome])
    cohort_frequencies: list[CohortFrequency] = Field(default_factory=list[CohortFrequency])
    source_refs: list[str] = Field(min_length=1)


class DiseaseAssociation(BaseModel):
    """Disease-to-pathway-node edge used by synchronized overlays."""

    model_config = ConfigDict(extra="forbid")

    disease_id: str = Field(min_length=1)
    pathway_node_id: str = Field(min_length=1)
    perturbation: PerturbationDirection
    tier: Tier
    species_evidence: list[SpeciesEvidence] = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)


class MutationRecord(BaseModel):
    """Normalized human mutation node linked to a pathway protein."""

    model_config = ConfigDict(extra="forbid")

    mutation_id: str = Field(min_length=1)
    gene_symbol: str = Field(min_length=1)
    hgvs_protein: str | None = None
    hgvs_coding: str
    clinical_significance: str | None = None
    oncogenicity: str | None = None
    functional_effect: FunctionalEffect
    tier: Tier
    species_evidence: list[SpeciesEvidence] = Field(min_length=1)
    sources: list[MutationSource] = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)
    cancer_frequencies: list[CohortFrequency] = Field(default_factory=list[CohortFrequency])
    cosmic_reconciliation: str | None = None

    @model_validator(mode="after")
    def hgvs_values_are_well_formed(self) -> "MutationRecord":
        """Reject mutation records that cannot be reconciled by HGVS."""

        if not HGVS_CODING_PATTERN.fullmatch(self.hgvs_coding):
            raise ValueError(f"invalid coding HGVS: {self.hgvs_coding}")
        if self.hgvs_protein and not HGVS_PROTEIN_PATTERN.fullmatch(self.hgvs_protein):
            raise ValueError(f"invalid protein HGVS: {self.hgvs_protein}")
        return self
