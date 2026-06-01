"""Curated Phase 2 node inventory and stable metadata.

The catalog intentionally stores biological identifiers separately from graph
construction. Protein accessions are resolved into a committed UniProt-derived
snapshot by ``mtor_nexus.ingest.uniprot_refresh``.
"""

from dataclasses import dataclass, field
from typing import cast

from mtor_nexus.drugs.catalog import DRUGS as PHARMACOLOGY_DRUGS
from mtor_nexus.schema import NodeType, SubcellularLocation

CORE = "01-core-complexes"
PI3K_AKT = "02-growth-factor-pi3k-akt"
TSC_RHEB = "03-tsc-rheb"
AMINO_ACID = "04-amino-acid-sensing"
ENERGY = "05-energy-sensing"
STRESS = "06-stress-inputs"
PROTEIN_SYNTHESIS = "07-protein-synthesis"
AUTOPHAGY = "08-autophagy"
LIPID_NUCLEOTIDE = "09-lipid-nucleotide-synthesis"
MTORC2 = "10-mtorc2-outputs"
CROSSTALK = "11-feedback-crosstalk"
DRUGS = "12-drugs"

SAxton_2017 = "10.1016/j.cell.2017.02.004"


@dataclass(frozen=True)
class ProteinSeed:
    """Compact catalog entry for a human protein node."""

    symbol: str
    module: str
    node_type: NodeType = NodeType.REGULATOR
    aliases: tuple[str, ...] = ()
    role: str = "Curated mTOR pathway protein."
    localization: tuple[SubcellularLocation, ...] = ()
    domains: tuple[str, ...] = ()
    pdb_ids: tuple[str, ...] = ()
    membership: tuple[str, ...] = ()


@dataclass(frozen=True)
class NonProteinSeed:
    """Catalog entry for complexes, conditions, metabolites, and drugs."""

    node_id: str
    module: str
    node_type: NodeType
    role: str
    aliases: tuple[str, ...] = ()
    chebi_id: str | None = None
    chembl_id: str | None = None
    localization: tuple[SubcellularLocation, ...] = ()
    pdb_ids: tuple[str, ...] = ()
    membership: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = field(default_factory=tuple)


KINASES = {
    "MTOR",
    "AKT1",
    "AKT2",
    "AKT3",
    "PDPK1",
    "PRKAA1",
    "PRKAA2",
    "CAMKK2",
    "EIF2AK3",
    "RPS6KB1",
    "RPS6KB2",
    "EEF2K",
    "ULK1",
    "ULK2",
    "PIK3C3",
    "PRKCA",
    "PRKCB",
    "PRKCG",
    "PRKCE",
    "PRKCZ",
    "SGK1",
    "MAPK1",
    "MAPK3",
    "RPS6KA1",
    "RPS6KA3",
    "GSK3B",
    "RAF1",
    "MAP2K1",
    "MAP2K2",
    "KDR",
    "MET",
    "PDGFRB",
    "FGFR1",
    "ERBB2",
    "IKBKB",
    "MAP3K7",
    "TBK1",
    "IKBKE",
    "CDK1",
    "CDK4",
    "CDK6",
}
RECEPTORS = {"INSR", "IGF1R", "EGFR", "KDR", "MET", "PDGFRB", "FGFR1", "ERBB2", "FZD1"}
GTPASES = {
    "RHEB",
    "RHEBL1",
    "RRAGA",
    "RRAGB",
    "RRAGC",
    "RRAGD",
    "RHOA",
    "RAC1",
    "CDC42",
    "HRAS",
    "KRAS",
    "NRAS",
}
SENSORS = {"SESN1", "SESN2", "SESN3", "CASTOR1", "CASTOR2", "SAMTOR", "SLC38A9", "LARS1"}
TRANSCRIPTION_FACTORS = {
    "ATF4",
    "FOXO1",
    "FOXO3",
    "HIF1A",
    "MITF",
    "MYC",
    "RELA",
    "SREBF1",
    "SREBF2",
    "STAT3",
    "TFEB",
    "TFE3",
    "TP53",
    "YAP1",
    "WWTR1",
}
PHOSPHATASES = {"PTEN", "PPP2CA", "PPP2CB", "PPP2R1A", "PPP2R2A", "PHLPP1", "PHLPP2"}
SCAFFOLDS = {"RPTOR", "RICTOR", "MAPKAP1", "MLST8", "YWHAZ", "RB1CC1", "ATG13", "ATG101"}


def _node_type(symbol: str) -> NodeType:
    """Infer a protein node category from curated symbol groups."""

    if symbol in RECEPTORS:
        return NodeType.RECEPTOR
    if symbol in KINASES:
        return NodeType.KINASE
    if symbol in GTPASES:
        return NodeType.GTPASE
    if symbol in SENSORS:
        return NodeType.SENSOR
    if symbol in TRANSCRIPTION_FACTORS:
        return NodeType.TRANSCRIPTION_FACTOR
    if symbol in PHOSPHATASES:
        return NodeType.PHOSPHATASE
    if symbol in SCAFFOLDS:
        return NodeType.SCAFFOLD
    return NodeType.REGULATOR


MODULE_PROTEINS = {
    CORE: """
        MTOR RPTOR MLST8 AKT1S1 DEPTOR RICTOR MAPKAP1 PRR5 PRR5L
    """,
    PI3K_AKT: """
        INSR IGF1R EGFR IRS1 IRS2 PIK3CA PIK3CB PIK3CD PIK3CG PIK3R1
        PIK3R2 PTEN PDPK1 AKT1 AKT2 AKT3 YWHAZ YWHAE
    """,
    TSC_RHEB: """
        TSC1 TSC2 TBC1D7 RHEB RHEBL1 TBC1D1 TBC1D4
    """,
    AMINO_ACID: """
        RRAGA RRAGB RRAGC RRAGD LAMTOR1 LAMTOR2 LAMTOR3 LAMTOR4 LAMTOR5
        DEPDC5 NPRL2 NPRL3 WDR24 WDR59 MIOS SEH1L SEC13 KPTN ITFG2 KICS2
        SZT2 SESN1 SESN2 SESN3 CASTOR1 CASTOR2 SAMTOR SLC38A9 LARS1 FLCN
        FNIP1 FNIP2 ATP6V1A ATP6V0D1 SLC7A5 SLC3A2
    """,
    ENERGY: """
        STK11 STRADA CAB39 CAMKK2 PRKAA1 PRKAA2 PRKAB1 PRKAB2 PRKAG1
        PRKAG2 PRKAG3
    """,
    STRESS: """
        DDIT4 HIF1A BNIP3 TP53 ATF4 EIF2AK3 ERN1 EIF2AK1 SESN2
    """,
    PROTEIN_SYNTHESIS: """
        RPS6KB1 RPS6KB2 RPS6 EIF4EBP1 EIF4EBP2 EIF4EBP3 EIF4E EIF4G1
        EIF4A1 EIF4B EEF2K EEF2 PDCD4 LARP1 RPS6KA1 RPS6KA3
    """,
    AUTOPHAGY: """
        ULK1 ULK2 ATG13 RB1CC1 ATG101 TFEB TFE3 MITF PIK3C3 BECN1 ATG14
        DAP NPC1 UVRAG WIPI2 SQSTM1 ATG5 ATG7 ATG12 MAP1LC3B
    """,
    LIPID_NUCLEOTIDE: """
        SREBF1 SREBF2 LPIN1 PPARG FASN ACACA CAD MTHFD2 DHODH PRPS1 ACLY
        HMGCR SCD ELOVL6
    """,
    MTORC2: """
        SGK1 PRKCA PRKCB PRKCG PRKCE PRKCZ PXN RHOA RAC1 CDC42 FOXO1 FOXO3
        NDRG1 PHLPP1 PHLPP2
    """,
    CROSSTALK: """
        GRB10 BTRC MAPK1 MAPK3 RPS6KA1 YAP1 WWTR1 GSK3B RELA NFKBIA RAF1
        MAP2K1 MAP2K2 HRAS KRAS NRAS CTNNB1 WNT3A FZD1 TSC22D1 IKBKB MAP3K7
        TBK1 IKBKE
        KDR VEGFA MET HGF PDGFRB PDGFB FGFR1 FGF2 ERBB2 NRG1 MYC STAT3 ESR1
        FOXK1 FOXK2 PPARGC1A RHOQ RAB1A RAB5A RAB7A RAB11A RAB34 ARL8B
        PPP2CA PPP2CB PPP2R1A PPP2R2A TRAF6 KLHL22 RNF152 SKP2 CUL1 FBXW11
        UBE2D1 UBE2D2 UBE2D3 CDK1 CDK4 CDK6 CCND1 CCNE1
    """,
    DRUGS: "FKBP1A",
}


SPECIAL_PROTEINS = {
    "MTOR": {
        "domains": ("HEAT", "FAT", "FRB", "kinase", "PRD", "FATC"),
        "pdb_ids": ("5H64", "4JSV", "6ZWM", "6ZWO"),
        "membership": ("MTORC1", "MTORC2"),
        "role": "Catalytic kinase shared by MTORC1 and MTORC2.",
    },
    "RPTOR": {"membership": ("MTORC1",), "role": "MTORC1 scaffold for TOS-motif substrates."},
    "RICTOR": {"membership": ("MTORC2",), "role": "MTORC2-defining scaffold."},
    "MLST8": {"membership": ("MTORC1", "MTORC2"), "role": "Shared mTOR-complex subunit."},
    "DEPTOR": {"pdb_ids": ("7PEC",)},
    "FLCN": {"pdb_ids": ("7UXH",)},
    "MAPKAP1": {"aliases": ("MSIN1",), "membership": ("MTORC2",)},
    "AKT1S1": {"aliases": ("PRAS40",), "membership": ("MTORC1",)},
    "STK11": {"aliases": ("LKB1",)},
    "CAB39": {"aliases": ("MO25",)},
    "RB1CC1": {"aliases": ("FIP200",)},
    "RPS6KB1": {"aliases": ("S6K1",)},
    "EIF4EBP1": {"aliases": ("4E-BP1",)},
    "FKBP1A": {"aliases": ("FKBP12",)},
}


def protein_seeds() -> list[ProteinSeed]:
    """Return unique protein nodes, keeping the first module assignment."""

    seeds: dict[str, ProteinSeed] = {}
    for module, symbols in MODULE_PROTEINS.items():
        for symbol in symbols.split():
            if symbol in seeds:
                continue
            special = SPECIAL_PROTEINS.get(symbol, {})
            seeds[symbol] = ProteinSeed(
                symbol=symbol,
                module=module,
                node_type=_node_type(symbol),
                aliases=cast(tuple[str, ...], special.get("aliases", ())),
                role=str(special.get("role", "Curated mTOR pathway protein.")),
                localization=cast(
                    tuple[SubcellularLocation, ...],
                    special.get("localization", ()),
                ),
                domains=cast(tuple[str, ...], special.get("domains", ())),
                pdb_ids=cast(tuple[str, ...], special.get("pdb_ids", ())),
                membership=cast(tuple[str, ...], special.get("membership", ())),
            )
    return list(seeds.values())


NON_PROTEIN_SEEDS = [
    NonProteinSeed(
        "MTORC1",
        CORE,
        NodeType.COMPLEX,
        "Nutrient-sensitive mTOR kinase complex.",
        pdb_ids=("5H64", "4JSV", "6SB2"),
    ),
    NonProteinSeed(
        "MTORC2",
        CORE,
        NodeType.COMPLEX,
        "Growth-factor-responsive mTOR kinase complex.",
        pdb_ids=("6ZWM", "6ZWO"),
    ),
    NonProteinSeed(
        "GATOR1", AMINO_ACID, NodeType.COMPLEX, "DEPDC5-NPRL2-NPRL3 GAP complex.", pdb_ids=("6CET",)
    ),
    NonProteinSeed(
        "GATOR2",
        AMINO_ACID,
        NodeType.COMPLEX,
        "Amino-acid signaling complex.",
        pdb_ids=("7UHY", "9LWF"),
    ),
    NonProteinSeed(
        "KICSTOR",
        AMINO_ACID,
        NodeType.COMPLEX,
        "Lysosomal GATOR1-recruitment complex.",
        pdb_ids=("9O5A",),
    ),
    NonProteinSeed("RAGULATOR", AMINO_ACID, NodeType.COMPLEX, "LAMTOR1-5 lysosomal Rag scaffold."),
    NonProteinSeed(
        "V-ATPASE", AMINO_ACID, NodeType.COMPLEX, "Vacuolar ATPase amino-acid signaling complex."
    ),
    NonProteinSeed(
        "AMPK", ENERGY, NodeType.COMPLEX, "Heterotrimeric AMP-activated protein kinase."
    ),
    NonProteinSeed(
        "TSC-COMPLEX",
        TSC_RHEB,
        NodeType.COMPLEX,
        "TSC1-TSC2-TBC1D7 GAP complex.",
        pdb_ids=("7DL2", "6SSH"),
    ),
    NonProteinSeed("14-3-3", PI3K_AKT, NodeType.COMPLEX, "Phosphoserine-binding 14-3-3 scaffold."),
    NonProteinSeed("AUTOPHAGY", AUTOPHAGY, NodeType.COMPLEX, "Autophagy output program."),
    NonProteinSeed("HYPOXIA", STRESS, NodeType.CONDITION, "Hypoxic cellular condition."),
    NonProteinSeed("DNA-DAMAGE", STRESS, NodeType.CONDITION, "DNA-damage cellular condition."),
    NonProteinSeed(
        "ER-STRESS", STRESS, NodeType.CONDITION, "Endoplasmic-reticulum stress condition."
    ),
    NonProteinSeed(
        "PIP2",
        PI3K_AKT,
        NodeType.LIPID,
        "Phosphatidylinositol 4,5-bisphosphate.",
        chebi_id="CHEBI:18348",
    ),
    NonProteinSeed(
        "PIP3",
        PI3K_AKT,
        NodeType.LIPID,
        "Phosphatidylinositol 3,4,5-trisphosphate.",
        chebi_id="CHEBI:16618",
    ),
    NonProteinSeed(
        "AMP", ENERGY, NodeType.METABOLITE, "Adenosine monophosphate.", chebi_id="CHEBI:16027"
    ),
    NonProteinSeed(
        "ATP", ENERGY, NodeType.METABOLITE, "Adenosine triphosphate.", chebi_id="CHEBI:15422"
    ),
    NonProteinSeed(
        "LEUCINE", AMINO_ACID, NodeType.METABOLITE, "L-leucine.", chebi_id="CHEBI:25017"
    ),
    NonProteinSeed(
        "ARGININE", AMINO_ACID, NodeType.METABOLITE, "L-arginine.", chebi_id="CHEBI:29016"
    ),
    NonProteinSeed(
        "SAM", AMINO_ACID, NodeType.METABOLITE, "S-adenosyl-L-methionine.", chebi_id="CHEBI:15414"
    ),
]


DRUG_SEEDS = [
    NonProteinSeed(
        node_id=drug.drug_id.upper(),
        module=DRUGS,
        node_type=NodeType.SMALL_MOLECULE,
        role=drug.mechanism,
        aliases=tuple(alias.upper() for alias in drug.aliases),
        chembl_id=drug.chembl_id,
        source_refs=tuple(drug.source_refs),
    )
    for drug in PHARMACOLOGY_DRUGS.values()
]
