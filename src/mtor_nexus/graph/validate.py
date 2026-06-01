"""Cross-source and release-gate validation for the Phase 2 graph."""

import argparse
import re
from collections import Counter
from dataclasses import asdict, dataclass

from mtor_nexus.drugs.catalog import DRUGS
from mtor_nexus.graph.build import DEFAULT_JSON
from mtor_nexus.graph.curated_edges import KEGG_ROOT, REACTOME_ROOT
from mtor_nexus.schema import EdgeMechanism, MTOREdge, RecruitmentMode, Tier
from mtor_nexus.utils.graph_io import validate_graph

DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$")


@dataclass(frozen=True)
class ValidationReport:
    """Summary of Phase 2 release criteria."""

    node_count: int
    edge_count: int
    mechanism_counts: dict[str, int]
    tier_distribution: dict[str, float]
    reactome_reconciliation: float
    kegg_reconciliation: float
    rodent_only_ratio: float
    single_source_edges: int


def _ratio(numerator: int, denominator: int) -> float:
    """Return a stable ratio for validation reports."""

    return numerator / denominator if denominator else 0.0


def _validate_recruitment_modes(edges: list[MTOREdge]) -> None:
    """Check the three distinct substrate-recruitment classes."""

    tos_targets = {
        edge.target
        for edge in edges
        if edge.source == "RPTOR" and edge.recruitment_mode == RecruitmentMode.TOS_MOTIF
    }
    if not {"RPS6KB1", "EIF4EBP1", "AKT1S1"} <= tos_targets:
        raise ValueError("RPTOR TOS-motif recruitment set is incomplete")
    if not any(edge.recruitment_mode == RecruitmentMode.MSIN1 for edge in edges):
        raise ValueError("mSIN1 recruitment mode is missing")
    if not any(
        edge.target == "TFEB" and edge.recruitment_mode == RecruitmentMode.FLCN_RAGC_GDP
        for edge in edges
    ):
        raise ValueError("TFEB FLCN-RagC-GDP recruitment mode is missing")


def validate_phase2_graph(path: str = DEFAULT_JSON) -> ValidationReport:
    """Validate hard Phase 2 graph invariants and return release metrics."""

    nodes, edges = validate_graph(path)
    if len(nodes) < 215:
        raise ValueError("Phase 2 graph requires at least 215 nodes")
    for edge in edges:
        if edge.mechanism == EdgeMechanism.PHOSPHORYLATES:
            if not edge.phosphositeplus_id:
                raise ValueError("phosphorylation edges require PhosphoSitePlus identifiers")
            if not any(DOI_PATTERN.match(citation) for citation in edge.citations):
                raise ValueError("phosphorylation edges require a DOI citation")
    _validate_recruitment_modes(edges)
    mechanism_counts = Counter(edge.mechanism.value for edge in edges)
    tier_counts = Counter(edge.tier.value for edge in edges)
    tier_distribution = {tier.value: _ratio(tier_counts[tier.value], len(edges)) for tier in Tier}
    drug_ids = {drug_id.upper() for drug_id in DRUGS}
    pathway_edges = [edge for edge in edges if edge.source not in drug_ids]
    reactome = _ratio(
        sum(REACTOME_ROOT in edge.source_refs for edge in pathway_edges), len(pathway_edges)
    )
    kegg = _ratio(sum(KEGG_ROOT in edge.source_refs for edge in pathway_edges), len(pathway_edges))
    report = ValidationReport(
        node_count=len(nodes),
        edge_count=len(edges),
        mechanism_counts=dict(sorted(mechanism_counts.items())),
        tier_distribution=tier_distribution,
        reactome_reconciliation=reactome,
        kegg_reconciliation=kegg,
        rodent_only_ratio=_ratio(
            sum(edge.species_evidence == ["rodent"] for edge in edges),
            len(edges),
        ),
        single_source_edges=sum(len(set(edge.evidence_sources)) < 2 for edge in edges),
    )
    if mechanism_counts[EdgeMechanism.PHOSPHORYLATES.value] < 70:
        raise ValueError("Phase 2 graph requires at least 70 phosphorylation edges")
    if report.reactome_reconciliation < 0.90:
        raise ValueError("Reactome root-pathway reconciliation is below 90%")
    if report.kegg_reconciliation < 0.85:
        raise ValueError("KEGG pathway reconciliation is below 85%")
    return report


def main() -> int:
    """Run the Phase 2 validator from the command line."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default=DEFAULT_JSON)
    args = parser.parse_args()
    report = validate_phase2_graph(args.graph)
    for key, value in asdict(report).items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
