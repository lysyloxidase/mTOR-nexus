"""Species provenance flags for graph evidence."""

from enum import StrEnum


class SpeciesEvidence(StrEnum):
    """Experimental context represented by an edge citation."""

    HUMAN = "human"
    RODENT = "rodent"
    HUMAN_AND_RODENT = "human_and_rodent"
    IN_VITRO_BIOCHEMICAL = "in_vitro_biochemical"
    STRUCTURAL = "structural"
    COMPUTATIONAL = "computational"
