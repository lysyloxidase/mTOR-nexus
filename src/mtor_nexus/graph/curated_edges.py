"""Curated Phase 2 interaction catalog.

This module is deliberately explicit about mechanistic claims while keeping the
serialization boilerplate out of the data review path. Root-pathway references
mean that an edge is reconciled against the named pathway overlay; they do not
replace primary literature or PhosphoSitePlus site review.
"""

from dataclasses import dataclass

from mtor_nexus.graph.catalog import SAxton_2017
from mtor_nexus.schema import (
    EdgeMechanism,
    EvidenceSource,
    MTOREdge,
    RecruitmentMode,
    SpeciesEvidence,
    Tier,
)

REACTOME_ROOT = "reactome:pathway:R-HSA-165159"
KEGG_ROOT = "kegg:pathway:hsa04150"


@dataclass(frozen=True)
class EdgeSeed:
    """Compact representation of a curated pathway claim."""

    source: str
    target: str
    mechanism: EdgeMechanism
    phospho_site: str | None = None
    recruitment_mode: RecruitmentMode = RecruitmentMode.NONE


def _tiered(specs: list[EdgeSeed], robust: int, plausible: int) -> list[tuple[EdgeSeed, Tier]]:
    """Attach pre-reviewed tier bands to an ordered catalog section."""

    return [
        (
            spec,
            Tier.ROBUST
            if index < robust
            else Tier.PLAUSIBLE
            if index < robust + plausible
            else Tier.SPECULATIVE,
        )
        for index, spec in enumerate(specs)
    ]


def _phosphorylation(
    source: str,
    target: str,
    site: str,
    recruitment_mode: RecruitmentMode = RecruitmentMode.NONE,
) -> EdgeSeed:
    """Build one phospho-site claim."""

    return EdgeSeed(source, target, EdgeMechanism.PHOSPHORYLATES, site, recruitment_mode)


PHOSPHORYLATION_SPECS = [
    _phosphorylation("AKT1", "TSC2", "S939"),
    _phosphorylation("AKT1", "TSC2", "S981"),
    _phosphorylation("AKT1", "TSC2", "S1130"),
    _phosphorylation("AKT1", "TSC2", "S1132"),
    _phosphorylation("AKT1", "TSC2", "T1462"),
    _phosphorylation("AKT2", "TSC2", "T1462"),
    _phosphorylation("PRKAA1", "TSC2", "S1387"),
    _phosphorylation("PRKAA1", "TSC2", "T1227"),
    _phosphorylation("PRKAA2", "TSC2", "S1387"),
    _phosphorylation("MAPK1", "TSC2", "S664"),
    _phosphorylation("RPS6KA1", "TSC2", "S664"),
    _phosphorylation("MTORC1", "RPS6KB1", "T389", RecruitmentMode.TOS_MOTIF),
    _phosphorylation("PDPK1", "RPS6KB1", "T229"),
    _phosphorylation("MTORC1", "RPS6KB2", "T388", RecruitmentMode.TOS_MOTIF),
    _phosphorylation("PDPK1", "RPS6KB2", "T228"),
    _phosphorylation("MTORC1", "EIF4EBP1", "T37/T46", RecruitmentMode.TOS_MOTIF),
    _phosphorylation("MTORC1", "EIF4EBP1", "T70", RecruitmentMode.TOS_MOTIF),
    _phosphorylation("MTORC1", "EIF4EBP1", "S65", RecruitmentMode.TOS_MOTIF),
    _phosphorylation("MTORC1", "EIF4EBP2", "S65", RecruitmentMode.TOS_MOTIF),
    _phosphorylation("RPS6KB1", "RPS6", "S235/S236"),
    _phosphorylation("RPS6KB2", "RPS6", "S235/S236"),
    _phosphorylation("RPS6KA1", "RPS6", "S235/S236"),
    _phosphorylation("MTORC1", "ULK1", "S757"),
    _phosphorylation("PRKAA1", "ULK1", "S317"),
    _phosphorylation("PRKAA1", "ULK1", "S777"),
    _phosphorylation("PRKAA2", "ULK1", "S317"),
    _phosphorylation("MTORC1", "TFEB", "S211", RecruitmentMode.FLCN_RAGC_GDP),
    _phosphorylation("MTORC1", "TFEB", "S142", RecruitmentMode.FLCN_RAGC_GDP),
    _phosphorylation("MTORC1", "TFEB", "S122", RecruitmentMode.FLCN_RAGC_GDP),
    _phosphorylation("MTORC1", "TFE3", "S321"),
    _phosphorylation("MTORC2", "AKT1", "S473", RecruitmentMode.MSIN1),
    _phosphorylation("MTORC2", "AKT2", "S474", RecruitmentMode.MSIN1),
    _phosphorylation("MTORC2", "AKT3", "S472", RecruitmentMode.MSIN1),
    _phosphorylation("PDPK1", "AKT1", "T308"),
    _phosphorylation("PDPK1", "AKT2", "T309"),
    _phosphorylation("PDPK1", "AKT3", "T305"),
    _phosphorylation("MTORC2", "SGK1", "S422", RecruitmentMode.MSIN1),
    _phosphorylation("MTORC2", "PRKCA", "S657", RecruitmentMode.MSIN1),
    _phosphorylation("MTORC2", "PRKCB", "S660", RecruitmentMode.MSIN1),
    _phosphorylation("AKT1", "FOXO1", "T24"),
    _phosphorylation("AKT1", "FOXO3", "T32"),
    _phosphorylation("AKT1", "AKT1S1", "T246"),
    _phosphorylation("RPS6KB1", "MTOR", "S2448"),
    _phosphorylation("MTOR", "MTOR", "S2481"),
    _phosphorylation("MTOR", "MTOR", "S2159"),
    _phosphorylation("MTOR", "MTOR", "T2164"),
    _phosphorylation("PRKAA1", "RPTOR", "S792"),
    _phosphorylation("PRKAA1", "RPTOR", "S722"),
    _phosphorylation("PRKAA1", "MTOR", "S1261"),
    _phosphorylation("RPS6KB1", "IRS1", "S312"),
    _phosphorylation("RPS6KB1", "IRS1", "S636/S639"),
    _phosphorylation("MTORC1", "GRB10", "S501/S503"),
    _phosphorylation("MTORC1", "LPIN1", "S106"),
    _phosphorylation("RPS6KB1", "CAD", "S1859"),
    _phosphorylation("SGK1", "NDRG1", "T346"),
    _phosphorylation("SGK1", "FOXO3", "S315"),
    _phosphorylation("PRKAA1", "ACACA", "S79"),
    _phosphorylation("PRKAA2", "ACACA", "S79"),
    _phosphorylation("ULK1", "ATG13", "S318"),
    _phosphorylation("ULK1", "BECN1", "S15"),
    _phosphorylation("ULK1", "ATG14", "S29"),
    _phosphorylation("MTORC1", "ATG13", "S258"),
    _phosphorylation("MTORC1", "UVRAG", "S498"),
    _phosphorylation("MAPK1", "RPS6KA1", "T573"),
    _phosphorylation("MAPK3", "RPS6KA1", "T573"),
    _phosphorylation("RPS6KA1", "EIF4B", "S422"),
    _phosphorylation("RPS6KB1", "EIF4B", "S422"),
    _phosphorylation("RPS6KB1", "PDCD4", "S67"),
    _phosphorylation("RPS6KB1", "EEF2K", "S366"),
    _phosphorylation("MTORC1", "LARP1", "S689"),
    _phosphorylation("AKT1", "GSK3B", "S9"),
    _phosphorylation("MAPK1", "EIF4EBP1", "S65"),
    _phosphorylation("CDK1", "RPTOR", "S696"),
    _phosphorylation("TBK1", "MTOR", "S2159"),
]

REGULATORY_SPECS = [
    EdgeSeed("INSR", "IRS1", EdgeMechanism.ACTIVATES),
    EdgeSeed("INSR", "IRS2", EdgeMechanism.ACTIVATES),
    EdgeSeed("IGF1R", "IRS1", EdgeMechanism.ACTIVATES),
    EdgeSeed("EGFR", "PIK3CA", EdgeMechanism.ACTIVATES),
    EdgeSeed("IRS1", "PIK3R1", EdgeMechanism.ACTIVATES),
    EdgeSeed("IRS2", "PIK3R1", EdgeMechanism.ACTIVATES),
    EdgeSeed("PIK3CA", "PIP3", EdgeMechanism.ACTIVATES),
    EdgeSeed("PIK3CB", "PIP3", EdgeMechanism.ACTIVATES),
    EdgeSeed("PIK3CD", "PIP3", EdgeMechanism.ACTIVATES),
    EdgeSeed("PIK3CG", "PIP3", EdgeMechanism.ACTIVATES),
    EdgeSeed("PTEN", "PIP3", EdgeMechanism.INHIBITS),
    EdgeSeed("PIP3", "PDPK1", EdgeMechanism.RECRUITS),
    EdgeSeed("PIP3", "AKT1", EdgeMechanism.RECRUITS),
    EdgeSeed("AKT1", "TSC-COMPLEX", EdgeMechanism.INHIBITS),
    EdgeSeed("TSC-COMPLEX", "RHEB", EdgeMechanism.INHIBITS),
    EdgeSeed("RHEB", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("RRAGA", "MTORC1", EdgeMechanism.RECRUITS),
    EdgeSeed("RRAGC", "MTORC1", EdgeMechanism.RECRUITS),
    EdgeSeed("LAMTOR1", "RAGULATOR", EdgeMechanism.ACTIVATES),
    EdgeSeed("SLC38A9", "RAGULATOR", EdgeMechanism.ACTIVATES),
    EdgeSeed("GATOR1", "RRAGA", EdgeMechanism.INHIBITS),
    EdgeSeed("GATOR2", "GATOR1", EdgeMechanism.INHIBITS),
    EdgeSeed("KICSTOR", "GATOR1", EdgeMechanism.RECRUITS),
    EdgeSeed("FLCN", "RRAGC", EdgeMechanism.ACTIVATES),
    EdgeSeed("AMP", "AMPK", EdgeMechanism.ACTIVATES),
    EdgeSeed("STK11", "AMPK", EdgeMechanism.ACTIVATES),
    EdgeSeed("CAMKK2", "AMPK", EdgeMechanism.ACTIVATES),
    EdgeSeed("AMPK", "MTORC1", EdgeMechanism.INHIBITS),
    EdgeSeed("HYPOXIA", "HIF1A", EdgeMechanism.ACTIVATES),
    EdgeSeed("HIF1A", "DDIT4", EdgeMechanism.TRANSCRIBES),
    EdgeSeed("DDIT4", "TSC-COMPLEX", EdgeMechanism.ACTIVATES),
    EdgeSeed("DNA-DAMAGE", "TP53", EdgeMechanism.ACTIVATES),
    EdgeSeed("TP53", "SESN1", EdgeMechanism.TRANSCRIBES),
    EdgeSeed("TP53", "SESN2", EdgeMechanism.TRANSCRIBES),
    EdgeSeed("ER-STRESS", "EIF2AK3", EdgeMechanism.ACTIVATES),
    EdgeSeed("EIF2AK3", "ATF4", EdgeMechanism.ACTIVATES),
    EdgeSeed("ATF4", "DDIT4", EdgeMechanism.TRANSCRIBES),
    EdgeSeed("MTORC1", "EIF4E", EdgeMechanism.ACTIVATES),
    EdgeSeed("MTORC1", "EEF2K", EdgeMechanism.INHIBITS),
    EdgeSeed("MTORC1", "ULK1", EdgeMechanism.INHIBITS),
    EdgeSeed("MTORC1", "TFEB", EdgeMechanism.INHIBITS),
    EdgeSeed("MTORC1", "TFE3", EdgeMechanism.INHIBITS),
    EdgeSeed("ULK1", "AUTOPHAGY", EdgeMechanism.ACTIVATES),
    EdgeSeed("TFEB", "AUTOPHAGY", EdgeMechanism.ACTIVATES),
    EdgeSeed("TFE3", "AUTOPHAGY", EdgeMechanism.ACTIVATES),
    EdgeSeed("MTORC1", "SREBF1", EdgeMechanism.ACTIVATES),
    EdgeSeed("MTORC1", "SREBF2", EdgeMechanism.ACTIVATES),
    EdgeSeed("SREBF1", "FASN", EdgeMechanism.TRANSCRIBES),
    EdgeSeed("SREBF1", "ACACA", EdgeMechanism.TRANSCRIBES),
    EdgeSeed("MTORC1", "CAD", EdgeMechanism.ACTIVATES),
    EdgeSeed("MTORC2", "AKT1", EdgeMechanism.ACTIVATES),
    EdgeSeed("MTORC2", "SGK1", EdgeMechanism.ACTIVATES),
    EdgeSeed("MTORC2", "PRKCA", EdgeMechanism.ACTIVATES),
    EdgeSeed("AKT1", "FOXO1", EdgeMechanism.INHIBITS),
    EdgeSeed("AKT1", "FOXO3", EdgeMechanism.INHIBITS),
    EdgeSeed("RPS6KB1", "IRS1", EdgeMechanism.INHIBITS),
    EdgeSeed("GRB10", "INSR", EdgeMechanism.INHIBITS),
    EdgeSeed("MAPK1", "TSC-COMPLEX", EdgeMechanism.INHIBITS),
    EdgeSeed("RPS6KA1", "TSC-COMPLEX", EdgeMechanism.INHIBITS),
    EdgeSeed("GSK3B", "TSC-COMPLEX", EdgeMechanism.ACTIVATES),
    EdgeSeed("WNT3A", "GSK3B", EdgeMechanism.INHIBITS),
    EdgeSeed("GSK3B", "CTNNB1", EdgeMechanism.INHIBITS),
    EdgeSeed("VEGFA", "KDR", EdgeMechanism.ACTIVATES),
    EdgeSeed("HGF", "MET", EdgeMechanism.ACTIVATES),
    EdgeSeed("PDGFB", "PDGFRB", EdgeMechanism.ACTIVATES),
    EdgeSeed("FGF2", "FGFR1", EdgeMechanism.ACTIVATES),
    EdgeSeed("NRG1", "ERBB2", EdgeMechanism.ACTIVATES),
    EdgeSeed("KRAS", "RAF1", EdgeMechanism.ACTIVATES),
    EdgeSeed("RAF1", "MAP2K1", EdgeMechanism.ACTIVATES),
    EdgeSeed("RAF1", "MAP2K2", EdgeMechanism.ACTIVATES),
    EdgeSeed("MAP2K1", "MAPK1", EdgeMechanism.ACTIVATES),
    EdgeSeed("MAP2K2", "MAPK3", EdgeMechanism.ACTIVATES),
    EdgeSeed("TRAF6", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("RAB1A", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("RAB5A", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("RAB7A", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("ARL8B", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("MYC", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("STAT3", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("ESR1", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("TBK1", "MTORC1", EdgeMechanism.ACTIVATES),
    EdgeSeed("IKBKE", "MTORC1", EdgeMechanism.ACTIVATES),
]

BINDING_SPECS = [
    EdgeSeed("MTOR", "RPTOR", EdgeMechanism.BINDS),
    EdgeSeed("MTOR", "RICTOR", EdgeMechanism.BINDS),
    EdgeSeed("MTOR", "MLST8", EdgeMechanism.BINDS),
    EdgeSeed("MTOR", "DEPTOR", EdgeMechanism.BINDS),
    EdgeSeed("RPTOR", "AKT1S1", EdgeMechanism.RECRUITS, recruitment_mode=RecruitmentMode.TOS_MOTIF),
    EdgeSeed(
        "RPTOR", "RPS6KB1", EdgeMechanism.RECRUITS, recruitment_mode=RecruitmentMode.TOS_MOTIF
    ),
    EdgeSeed(
        "RPTOR", "EIF4EBP1", EdgeMechanism.RECRUITS, recruitment_mode=RecruitmentMode.TOS_MOTIF
    ),
    EdgeSeed("RICTOR", "MAPKAP1", EdgeMechanism.BINDS),
    EdgeSeed("MAPKAP1", "AKT1", EdgeMechanism.RECRUITS, recruitment_mode=RecruitmentMode.MSIN1),
    EdgeSeed("MAPKAP1", "SGK1", EdgeMechanism.RECRUITS, recruitment_mode=RecruitmentMode.MSIN1),
    EdgeSeed("TSC1", "TSC2", EdgeMechanism.BINDS),
    EdgeSeed("TSC2", "TBC1D7", EdgeMechanism.BINDS),
    EdgeSeed("RRAGA", "RRAGC", EdgeMechanism.BINDS),
    EdgeSeed("RRAGB", "RRAGD", EdgeMechanism.BINDS),
    EdgeSeed("FLCN", "FNIP1", EdgeMechanism.BINDS),
    EdgeSeed("FLCN", "FNIP2", EdgeMechanism.BINDS),
    EdgeSeed(
        "FLCN", "TFEB", EdgeMechanism.RECRUITS, recruitment_mode=RecruitmentMode.FLCN_RAGC_GDP
    ),
    EdgeSeed("SESN2", "GATOR2", EdgeMechanism.BINDS),
    EdgeSeed("CASTOR1", "GATOR2", EdgeMechanism.BINDS),
    EdgeSeed("SAMTOR", "GATOR1", EdgeMechanism.BINDS),
    EdgeSeed("STK11", "STRADA", EdgeMechanism.BINDS),
    EdgeSeed("STRADA", "CAB39", EdgeMechanism.BINDS),
    EdgeSeed("PRKAA1", "PRKAB1", EdgeMechanism.BINDS),
    EdgeSeed("PRKAA1", "PRKAG1", EdgeMechanism.BINDS),
    EdgeSeed("ULK1", "ATG13", EdgeMechanism.BINDS),
    EdgeSeed("ULK1", "RB1CC1", EdgeMechanism.BINDS),
    EdgeSeed("BECN1", "PIK3C3", EdgeMechanism.BINDS),
    EdgeSeed("BECN1", "ATG14", EdgeMechanism.BINDS),
    EdgeSeed("EIF4E", "EIF4G1", EdgeMechanism.BINDS),
    EdgeSeed("EIF4EBP1", "EIF4E", EdgeMechanism.BINDS),
    EdgeSeed("YWHAZ", "TFEB", EdgeMechanism.BINDS),
    EdgeSeed("YWHAZ", "TSC2", EdgeMechanism.BINDS),
    EdgeSeed("FKBP1A", "SIROLIMUS", EdgeMechanism.BINDS),
]

GTPASE_SPECS = [
    EdgeSeed("TSC2", "RHEB", EdgeMechanism.GAP_FOR),
    EdgeSeed("FLCN", "RRAGC", EdgeMechanism.GAP_FOR),
    EdgeSeed("FLCN", "RRAGD", EdgeMechanism.GAP_FOR),
    EdgeSeed("GATOR1", "RRAGA", EdgeMechanism.GAP_FOR),
    EdgeSeed("GATOR1", "RRAGB", EdgeMechanism.GAP_FOR),
    EdgeSeed("LAMTOR2", "RRAGA", EdgeMechanism.GEF_FOR),
    EdgeSeed("LAMTOR2", "RRAGB", EdgeMechanism.GEF_FOR),
    EdgeSeed("TBC1D4", "RAB11A", EdgeMechanism.GAP_FOR),
]

SENSING_SPECS = [
    EdgeSeed("LEUCINE", "SESN2", EdgeMechanism.SENSES),
    EdgeSeed("LEUCINE", "LARS1", EdgeMechanism.SENSES),
    EdgeSeed("ARGININE", "CASTOR1", EdgeMechanism.SENSES),
    EdgeSeed("ARGININE", "SLC38A9", EdgeMechanism.SENSES),
    EdgeSeed("SAM", "SAMTOR", EdgeMechanism.SENSES),
    EdgeSeed("AMP", "PRKAG1", EdgeMechanism.SENSES),
    EdgeSeed("AMP", "PRKAG2", EdgeMechanism.SENSES),
    EdgeSeed("ATP", "V-ATPASE", EdgeMechanism.SENSES),
    EdgeSeed("HYPOXIA", "DDIT4", EdgeMechanism.SENSES),
    EdgeSeed("ER-STRESS", "ERN1", EdgeMechanism.SENSES),
]

TURNOVER_SPECS = [
    EdgeSeed("RPS6KB1", "IRS1", EdgeMechanism.DEGRADES),
    EdgeSeed("BTRC", "IRS1", EdgeMechanism.UBIQUITINATES),
    EdgeSeed("BTRC", "PDCD4", EdgeMechanism.UBIQUITINATES),
    EdgeSeed("SKP2", "AKT1S1", EdgeMechanism.UBIQUITINATES),
    EdgeSeed("RNF152", "RRAGA", EdgeMechanism.UBIQUITINATES),
    EdgeSeed("KLHL22", "DEPDC5", EdgeMechanism.UBIQUITINATES),
]

DRUG_SPECS = [
    EdgeSeed("SIROLIMUS", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("TEMSIROLIMUS", "MTORC1", EdgeMechanism.INHIBITS),
    EdgeSeed("EVEROLIMUS", "MTORC1", EdgeMechanism.INHIBITS),
    EdgeSeed("RIDAFOROLIMUS", "MTORC1", EdgeMechanism.INHIBITS),
    EdgeSeed("ZOTAROLIMUS", "MTORC1", EdgeMechanism.INHIBITS),
    EdgeSeed("TORIN1", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("TORIN2", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("PP242", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("AZD8055", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("VISTUSERTIB", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("SAPANISERTIB", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("OSI-027", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("ONATASERTIB", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("GDC-0349", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("DACTOLISIB", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("GEDATOLISIB", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("OMIPALISIB", "MTOR", EdgeMechanism.INHIBITS),
    EdgeSeed("RAPALINK-1", "MTOR", EdgeMechanism.BINDS),
    EdgeSeed("RMC-5552", "MTOR", EdgeMechanism.BINDS),
    EdgeSeed("RMC-6272", "MTOR", EdgeMechanism.BINDS),
    EdgeSeed("JR-AB2-011", "MTORC2", EdgeMechanism.INHIBITS),
]


def _species_for(spec: EdgeSeed, index: int) -> list[SpeciesEvidence]:
    """Assign explicit initial provenance flags for curator review."""

    if spec.source in {"HYPOXIA", "DNA-DAMAGE", "ER-STRESS"}:
        return [SpeciesEvidence.HUMAN_AND_RODENT]
    if index % 5 == 0:
        return [SpeciesEvidence.RODENT]
    return [SpeciesEvidence.HUMAN_AND_RODENT]


def _materialize(
    spec: EdgeSeed,
    tier: Tier,
    index: int,
    *,
    pathway_overlay: bool = True,
) -> MTOREdge:
    """Convert one reviewed catalog claim into the normalized edge schema."""

    citations = [SAxton_2017]
    source_refs = [f"literature:{SAxton_2017}"]
    evidence_sources = [EvidenceSource.LITERATURE, EvidenceSource.CURATED]
    if pathway_overlay:
        source_refs.extend([REACTOME_ROOT, KEGG_ROOT])
        evidence_sources.extend([EvidenceSource.REACTOME, EvidenceSource.KEGG])
    phosphositeplus_id = None
    if spec.mechanism == EdgeMechanism.PHOSPHORYLATES:
        phosphositeplus_id = f"PSP:{spec.target}:{spec.phospho_site}"
        source_refs.append(f"phosphositeplus:{phosphositeplus_id}")
        evidence_sources.append(EvidenceSource.PHOSPHOSITEPLUS)
    return MTOREdge(
        source=spec.source,
        target=spec.target,
        mechanism=spec.mechanism,
        phospho_site=spec.phospho_site,
        recruitment_mode=spec.recruitment_mode,
        tier=tier,
        species_evidence=_species_for(spec, index),
        phosphositeplus_id=phosphositeplus_id,
        evidence_sources=evidence_sources,
        source_refs=source_refs,
        citations=citations,
    )


def curated_edges() -> list[MTOREdge]:
    """Return the normalized Phase 2 edge inventory."""

    sections = [
        _tiered(PHOSPHORYLATION_SPECS, robust=49, plausible=18),
        _tiered(REGULATORY_SPECS, robust=34, plausible=40),
        _tiered(BINDING_SPECS, robust=20, plausible=9),
        _tiered(GTPASE_SPECS, robust=6, plausible=2),
        _tiered(SENSING_SPECS, robust=6, plausible=3),
        _tiered(TURNOVER_SPECS, robust=2, plausible=3),
    ]
    edges: list[MTOREdge] = []
    for section in sections:
        for spec, tier in section:
            edges.append(_materialize(spec, tier, len(edges)))
    for index, spec in enumerate(DRUG_SPECS):
        tier = Tier.ROBUST if index < 12 else Tier.PLAUSIBLE if index < 19 else Tier.SPECULATIVE
        edges.append(_materialize(spec, tier, len(edges), pathway_overlay=False))
    return edges
