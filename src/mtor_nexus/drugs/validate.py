"""Release gates for the Phase 5 inhibitor pharmacology layer."""

from dataclasses import asdict, dataclass

from mtor_nexus.drugs.bioactivity import smiles_is_parseable
from mtor_nexus.drugs.catalog import (
    COUNTER_SCREEN_TARGETS,
    DRUGS,
    GENERATIONS,
    RESISTANCE_MUTATIONS,
    drug_target_links,
)
from mtor_nexus.drugs.export import drug_document
from mtor_nexus.drugs.models import DrugDocument
from mtor_nexus.utils.nomenclature import RAS_ON_INHIBITORS


@dataclass(frozen=True)
class Phase5Validation:
    """Summary of Phase 5 inhibitor-layer release criteria."""

    generation_count: int
    drug_count: int
    target_link_count: int
    counter_screen_target_count: int
    bioactivity_label_count: int
    compounds_with_labels: int
    resistance_mutation_count: int


def validate_phase5_layer() -> Phase5Validation:
    """Validate inhibitor catalog, target edges, structures, and training labels."""

    document = DrugDocument.model_validate(drug_document())
    drugs = list(DRUGS.values())
    links = drug_target_links()
    if len(GENERATIONS) != 5:
        raise ValueError("Phase 5 requires five inhibitor classes")
    if any(not drug.chembl_id for drug in drugs):
        raise ValueError("every inhibitor node requires a ChEMBL identifier")
    sapanisertib = DRUGS["sapanisertib"]
    if set(sapanisertib.aliases) < {"MLN0128", "INK128", "TAK-228"}:
        raise ValueError("sapanisertib aliases are not unified")
    if set(DRUGS) & {inhibitor.lower() for inhibitor in RAS_ON_INHIBITORS}:
        raise ValueError("RAS(ON) compounds cannot enter the mTOR inhibitor catalog")
    if DRUGS["rmc-5552"].potency != (
        "pS6K IC50 0.14 nM; p4EBP1 IC50 0.48 nM; pAKT IC50 19 nM (~40x mTORC1/2 selectivity)"
    ):
        raise ValueError("RMC-5552 potency annotation drifted")
    if {target.gene_symbol for target in COUNTER_SCREEN_TARGETS} != {
        "MTOR",
        "PIK3CA",
        "ATM",
        "ATR",
        "PRKDC",
    }:
        raise ValueError("PIKK counter-screen target panel is incomplete")
    if {mutation.mutation_id for mutation in RESISTANCE_MUTATIONS} != {
        "A2034V",
        "F2108L",
        "M2327I",
    }:
        raise ValueError("resistance mutation annotations are incomplete")
    if {link.drug_id for link in links} != set(DRUGS):
        raise ValueError("every inhibitor requires at least one mechanism edge")
    if any(not link.species_evidence or not link.tier for link in links):
        raise ValueError("every inhibitor mechanism edge requires tier and species tags")
    compounds = document.bioactivity
    if {compound.drug_id for compound in compounds} != set(DRUGS):
        raise ValueError("every inhibitor requires an RDKit-standardized structure")
    if any(not smiles_is_parseable(compound.rdkit_standardized_smiles) for compound in compounds):
        raise ValueError("RDKit-standardized snapshot contains an unparseable SMILES")
    activities = [activity for compound in compounds for activity in compound.activities]
    if {activity.target_gene_symbol for activity in activities} < {
        "MTOR",
        "PIK3CA",
        "ATM",
        "ATR",
        "PRKDC",
    }:
        raise ValueError("ChEMBL snapshot does not retain all PIKK counter-screen labels")
    return Phase5Validation(
        generation_count=len(GENERATIONS),
        drug_count=len(drugs),
        target_link_count=len(links),
        counter_screen_target_count=len(COUNTER_SCREEN_TARGETS),
        bioactivity_label_count=len(activities),
        compounds_with_labels=sum(bool(compound.activities) for compound in compounds),
        resistance_mutation_count=len(RESISTANCE_MUTATIONS),
    )


def main() -> int:
    """Run Phase 5 inhibitor-layer validation."""

    for key, value in asdict(validate_phase5_layer()).items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
