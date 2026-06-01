"""Typed inhibitor-catalog, target-link, and ChEMBL bioactivity models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from mtor_nexus.schema import EdgeMechanism, SpeciesEvidence, Tier


class BindingMode(StrEnum):
    """Structural mode by which an inhibitor perturbs mTOR signaling."""

    FRB_ALLOSTERIC = "frb_allosteric"
    ATP_COMPETITIVE = "atp_competitive"
    DUAL_PI3K_MTOR_ATP = "dual_pi3k_mtor_atp"
    BISTERIC_FRB_ATP = "bisteric_frb_atp"
    RICTOR_MTOR_ASSOCIATION = "rictor_mtor_association"


class DrugGeneration(BaseModel):
    """One pharmacological class displayed by the binding-mode viewer."""

    model_config = ConfigDict(extra="forbid")

    generation_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    mechanism: str = Field(min_length=1)
    binding_mode: BindingMode
    binding_site: str = Field(min_length=1)
    drug_ids: list[str] = Field(min_length=1)
    limitation: str | None = None
    advantage: str | None = None
    co_receptor: str | None = None


class DrugRecord(BaseModel):
    """One alias-normalized inhibitor node."""

    model_config = ConfigDict(extra="forbid")

    drug_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    generation_id: str = Field(min_length=1)
    chembl_id: str = Field(pattern=r"^CHEMBL\d+$")
    aliases: list[str] = Field(default_factory=list[str])
    mechanism: str = Field(min_length=1)
    approvals: list[str] = Field(default_factory=list[str])
    trials: list[str] = Field(default_factory=list[str])
    status: str | None = None
    use: str | None = None
    off_target: str | None = None
    doi: str | None = None
    potency: str | None = None
    cns_penetrant: bool = False
    caveat: str | None = None
    source_refs: list[str] = Field(min_length=1)


class DrugTargetLink(BaseModel):
    """Mechanistic inhibitor-to-pathway-node edge."""

    model_config = ConfigDict(extra="forbid")

    drug_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    mechanism: EdgeMechanism
    binding_mode: BindingMode
    tier: Tier
    species_evidence: list[SpeciesEvidence] = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)


class StructuralSite(BaseModel):
    """Structural site and resistance-residue annotation for the viewer."""

    model_config = ConfigDict(extra="forbid")

    site_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    pdb_id: str = Field(pattern=r"^[0-9][A-Za-z0-9]{3}$")
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    description: str = Field(min_length=1)


class ResistanceMutation(BaseModel):
    """Resistance mutation positioned in an mTOR structural site."""

    model_config = ConfigDict(extra="forbid")

    mutation_id: str = Field(pattern=r"^[A-Z]\d+[A-Z]$")
    domain: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    effect: str = Field(min_length=1)
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    source_refs: list[str] = Field(min_length=1)


class ChemblTarget(BaseModel):
    """ChEMBL target included in the Phase 6 counter-screen panel."""

    model_config = ConfigDict(extra="forbid")

    gene_symbol: str = Field(min_length=1)
    chembl_id: str = Field(pattern=r"^CHEMBL\d+$")
    preferred_name: str = Field(min_length=1)


class AssayMetadata(BaseModel):
    """Compact assay provenance retained with each ChEMBL activity."""

    model_config = ConfigDict(extra="forbid")

    assay_chembl_id: str = Field(pattern=r"^CHEMBL\d+$")
    assay_type: str = Field(min_length=1)
    description: str = Field(min_length=1)
    confidence_score: int = Field(ge=0, le=9)


class BioactivityRecord(BaseModel):
    """One standardized ChEMBL IC50, Ki, or Kd training label."""

    model_config = ConfigDict(extra="forbid")

    activity_id: int = Field(gt=0)
    drug_id: str = Field(min_length=1)
    molecule_chembl_id: str = Field(pattern=r"^CHEMBL\d+$")
    target_gene_symbol: str = Field(min_length=1)
    target_chembl_id: str = Field(pattern=r"^CHEMBL\d+$")
    standard_type: str = Field(pattern=r"^(IC50|Ki|Kd)$")
    standard_relation: str = Field(min_length=1)
    standard_value: float = Field(ge=0)
    standard_units: str = Field(min_length=1)
    assay: AssayMetadata


class CompoundBioactivity(BaseModel):
    """RDKit-standardized molecular structure and linked training labels."""

    model_config = ConfigDict(extra="forbid")

    drug_id: str = Field(min_length=1)
    molecule_chembl_id: str = Field(pattern=r"^CHEMBL\d+$")
    canonical_smiles: str = Field(min_length=1)
    rdkit_standardized_smiles: str = Field(min_length=1)
    activities: list[BioactivityRecord] = Field(default_factory=list[BioactivityRecord])


class DrugDocument(BaseModel):
    """Public Phase 5 export consumed by the API and browser."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(min_length=1)
    metadata: dict[str, str | bool | int]
    generations: list[DrugGeneration] = Field(min_length=1)
    drugs: list[DrugRecord] = Field(min_length=1)
    target_links: list[DrugTargetLink] = Field(min_length=1)
    structural_sites: list[StructuralSite] = Field(min_length=1)
    resistance_mutations: list[ResistanceMutation] = Field(min_length=1)
    counter_screen_targets: list[ChemblTarget] = Field(min_length=1)
    bioactivity: list[CompoundBioactivity] = Field(min_length=1)

    @model_validator(mode="after")
    def references_are_resolvable(self) -> "DrugDocument":
        """Keep catalog references and training rows inside the exported layer."""

        drug_ids = {drug.drug_id for drug in self.drugs}
        site_ids = {site.site_id for site in self.structural_sites}
        target_ids = {target.chembl_id for target in self.counter_screen_targets}
        if (
            missing := {drug_id for group in self.generations for drug_id in group.drug_ids}
            - drug_ids
        ):
            raise ValueError(f"generation references unknown drugs: {sorted(missing)}")
        if missing := {link.drug_id for link in self.target_links} - drug_ids:
            raise ValueError(f"target links reference unknown drugs: {sorted(missing)}")
        if missing := {mutation.site_id for mutation in self.resistance_mutations} - site_ids:
            raise ValueError(f"resistance mutations reference unknown sites: {sorted(missing)}")
        for compound in self.bioactivity:
            if compound.drug_id not in drug_ids:
                raise ValueError(f"bioactivity references unknown drug: {compound.drug_id}")
            if (
                missing := {activity.target_chembl_id for activity in compound.activities}
                - target_ids
            ):
                raise ValueError(f"bioactivity references unknown targets: {sorted(missing)}")
        return self
