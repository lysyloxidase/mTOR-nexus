"""Release gates for the Phase 4 disease and mutation layer."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mtor_nexus.disease.classes import DISEASE_CLASSES, disease_associations
from mtor_nexus.disease.mutations import curated_mutations
from mtor_nexus.schema import SpeciesEvidence

REQUIRED_MUTATION_GENES = {
    "PIK3CA",
    "PTEN",
    "AKT1",
    "TSC1",
    "TSC2",
    "MTOR",
    "DEPDC5",
    "STK11",
    "STRADA",
}


@dataclass(frozen=True)
class Phase4Validation:
    """Summary of Phase 4 disease-layer release criteria."""

    disease_class_count: int
    association_count: int
    mutation_count: int
    mutation_gene_count: int
    rare_syndrome_count: int


def validate_phase4_layer(
    graph_path: str = "data/processed/mtor-graph.json",
) -> Phase4Validation:
    """Validate disease mappings, mutation records, and clinical annotations."""

    graph: dict[str, Any] = json.loads(Path(graph_path).read_text(encoding="utf-8"))
    pathway_nodes = {node["node_id"] for node in graph["nodes"]}
    diseases = list(DISEASE_CLASSES.values())
    associations = disease_associations()
    mutations = curated_mutations()
    if len(diseases) != 8:
        raise ValueError("Phase 4 requires exactly eight disease classes")
    disease_node_ids = {node_id for disease in diseases for node_id in disease.key_nodes}
    if missing := disease_node_ids - pathway_nodes:
        raise ValueError(f"disease overlay nodes missing from pathway graph: {sorted(missing)}")
    if missing := REQUIRED_MUTATION_GENES - {mutation.gene_symbol for mutation in mutations}:
        raise ValueError(f"required mutation genes missing: {sorted(missing)}")
    if any(
        not association.species_evidence or not association.tier for association in associations
    ):
        raise ValueError("every disease association requires tier and species evidence")
    rare = DISEASE_CLASSES["rare_syndromes"]
    if len(rare.rare_syndromes) != 6:
        raise ValueError("rare syndrome overlay requires six syndromes")
    drug_pairs = {(drug.name, drug.indication) for drug in rare.approved_drugs}
    if not any(name == "everolimus" and "TSC" in indication for name, indication in drug_pairs):
        raise ValueError("everolimus TSC annotation missing")
    if not any(
        name == "sirolimus" and "lymphangioleiomyomatosis" in indication
        for name, indication in drug_pairs
    ):
        raise ValueError("sirolimus LAM annotation missing")
    for disease_id in ["aging_longevity", "metabolic"]:
        if not DISEASE_CLASSES[disease_id].species_caveat:
            raise ValueError(f"{disease_id} requires a species caveat")
    if not all(mutation.species_evidence == [SpeciesEvidence.HUMAN] for mutation in mutations):
        raise ValueError("mutation nodes must retain human-genetics provenance")
    return Phase4Validation(
        disease_class_count=len(diseases),
        association_count=len(associations),
        mutation_count=len(mutations),
        mutation_gene_count=len({mutation.gene_symbol for mutation in mutations}),
        rare_syndrome_count=len(rare.rare_syndromes),
    )


def main() -> int:
    """Run the Phase 4 disease-layer validator."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="data/processed/mtor-graph.json")
    args = parser.parse_args()
    report = validate_phase4_layer(args.graph)
    for key, value in report.__dict__.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
