"""Hard guards against recurring mTOR nomenclature errors."""

from collections.abc import Iterable

from mtor_nexus.schema import MTOREdge, MTORNode

RAS_ON_INHIBITORS = {"RMC-6236", "RMC-6291", "RMC-9805"}
SAPANISERTIB_ALIASES = {"MLN0128", "INK128", "TAK-228"}


def validate_nomenclature(nodes: Iterable[MTORNode], edges: Iterable[MTOREdge]) -> None:
    """Reject known compound and phosphorylation attribution mistakes."""

    node_list = list(nodes)
    edge_list = list(edges)
    errors: list[str] = []
    for node in node_list:
        aliases = set(node.aliases)
        identifiers = {node.node_id, *aliases}
        if identifiers & RAS_ON_INHIBITORS and "mtor" in node.pathway_role.lower():
            errors.append(f"{node.node_id}: RAS(ON) inhibitor must not be tagged as an mTOR drug")
        if node.node_id == "SAPANISERTIB" and not aliases >= SAPANISERTIB_ALIASES:
            errors.append("SAPANISERTIB: MLN0128, INK128, and TAK-228 aliases must be unified")

    for edge in edge_list:
        site = (edge.phospho_site or "").upper()
        if edge.source == "AKT1" and edge.target == "MTOR" and site == "S2448":
            errors.append("AKT1 -> MTOR S2448 is forbidden; attribute feedback to RPS6KB1")
        if edge.target == "TSC2" and site == "S1462":
            errors.append("TSC2 S1462 is invalid; the canonical AKT site is T1462")
        if edge.target == "MTOR" and site == "S2481" and edge.source != "MTOR":
            errors.append("MTOR S2481 must be encoded as MTOR autophosphorylation")

    if errors:
        raise ValueError("; ".join(errors))
