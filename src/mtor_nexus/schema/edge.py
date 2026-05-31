"""Edge model for evidence-aware mTOR pathway interactions."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mtor_nexus.schema.source import EvidenceSource
from mtor_nexus.schema.species import SpeciesEvidence
from mtor_nexus.schema.tier import Tier


class EdgeMechanism(StrEnum):
    """Mechanistic relationship encoded by an edge."""

    ACTIVATES = "activates"
    INHIBITS = "inhibits"
    PHOSPHORYLATES = "phosphorylates"
    DEPHOSPHORYLATES = "dephosphorylates"
    BINDS = "binds"
    GAP_FOR = "gap_for"
    GEF_FOR = "gef_for"
    UBIQUITINATES = "ubiquitinates"
    DEGRADES = "degrades"
    RECRUITS = "recruits"
    SENSES = "senses"
    TRANSCRIBES = "transcribes"


class RecruitmentMode(StrEnum):
    """Distinct substrate recruitment classes represented by the atlas."""

    TOS_MOTIF = "tos_motif"
    MSIN1 = "msin1"
    FLCN_RAGC_GDP = "flcn_ragc_gdp"
    NONE = "none"


class MTOREdge(BaseModel):
    """A directed graph edge with non-optional evidence provenance."""

    model_config = ConfigDict(extra="forbid")

    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    mechanism: EdgeMechanism
    directionality: bool = True
    phospho_site: str | None = None
    recruitment_mode: RecruitmentMode = RecruitmentMode.NONE
    tier: Tier
    species_evidence: list[SpeciesEvidence] = Field(min_length=1)
    phosphositeplus_id: str | None = None
    evidence_sources: list[EvidenceSource] = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)
    citations: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def phosphorylation_edges_have_site_identifiers(self) -> "MTOREdge":
        """Keep phosphorylation edges resolvable to a documented site."""

        if self.mechanism == EdgeMechanism.PHOSPHORYLATES:
            if not self.phospho_site:
                raise ValueError("phosphorylation edges require a phospho-site")
            if not self.phosphositeplus_id:
                raise ValueError("phosphorylation edges require a PhosphoSitePlus identifier")
        return self
