"""Regression tests for hard mTOR nomenclature constraints."""

import pytest

from mtor_nexus.schema import EdgeMechanism, MTOREdge, MTORNode, NodeType, SpeciesEvidence, Tier
from mtor_nexus.utils.graph_io import validate_graph
from mtor_nexus.utils.nomenclature import validate_nomenclature


def molecule(node_id: str, role: str, aliases: list[str] | None = None) -> MTORNode:
    """Build a compact molecule node for guard tests."""

    return MTORNode(
        node_id=node_id,
        protein_name=node_id,
        node_type=NodeType.SMALL_MOLECULE,
        pathway_role=role,
        aliases=aliases or [],
        primary_citations=["10.1016/j.cell.2017.02.004"],
    )


def phospho_edge(source: str, target: str, site: str) -> MTOREdge:
    """Build a valid phosphorylation edge for guard tests."""

    return MTOREdge(
        source=source,
        target=target,
        mechanism=EdgeMechanism.PHOSPHORYLATES,
        phospho_site=site,
        tier=Tier.ROBUST,
        species_evidence=[SpeciesEvidence.HUMAN],
        phosphositeplus_id=f"PSP:{target}:{site}",
        citations=["10.1016/j.cell.2017.02.004"],
    )


@pytest.mark.parametrize("compound", ["RMC-6236", "RMC-6291", "RMC-9805"])
def test_ras_on_compounds_cannot_be_tagged_as_mtor_drugs(compound: str) -> None:
    """Keep Revolution Medicines RAS(ON) inhibitors out of the mTOR drug set."""

    with pytest.raises(ValueError, match="RAS\\(ON\\)"):
        validate_nomenclature([molecule(compound, "bi-steric mTOR inhibitor")], [])


def test_mtor_s2448_is_not_attributed_to_akt() -> None:
    """Encode S2448 as S6K1 feedback rather than an AKT target."""

    with pytest.raises(ValueError, match="S2448"):
        validate_nomenclature([], [phospho_edge("AKT1", "MTOR", "S2448")])


def test_tsc2_s1462_typo_is_rejected() -> None:
    """Protect canonical TSC2 T1462 from a serine typo."""

    with pytest.raises(ValueError, match="T1462"):
        validate_nomenclature([], [phospho_edge("AKT1", "TSC2", "S1462")])


def test_mtor_s2481_must_be_autophosphorylation() -> None:
    """Reject external kinase attribution for mTOR S2481."""

    with pytest.raises(ValueError, match="autophosphorylation"):
        validate_nomenclature([], [phospho_edge("AKT1", "MTOR", "S2481")])


def test_sapanisertib_alias_set_is_required() -> None:
    """Unify the known names for sapanisertib into one node."""

    with pytest.raises(ValueError, match="aliases"):
        validate_nomenclature([molecule("SAPANISERTIB", "ATP-competitive inhibitor")], [])


def test_seed_graph_passes_nomenclature_guards() -> None:
    """Exercise the guards against the committed seed graph."""

    validate_graph("data/processed/mtor-graph.json")
