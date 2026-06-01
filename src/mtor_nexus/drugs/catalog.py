"""Alias-normalized three-generation mTOR inhibitor catalog."""

import re

from mtor_nexus.drugs.models import (
    BindingMode,
    ChemblTarget,
    DrugGeneration,
    DrugRecord,
    DrugTargetLink,
    ResistanceMutation,
    StructuralSite,
)
from mtor_nexus.schema import EdgeMechanism, SpeciesEvidence, Tier

NATURE_RAPALINK = "10.1038/nature17963"
JMEDCHEM_RMC5552 = "10.1021/acs.jmedchem.2c01658"

COUNTER_SCREEN_TARGETS = [
    ChemblTarget(
        gene_symbol="MTOR",
        chembl_id="CHEMBL2842",
        preferred_name="Serine/threonine-protein kinase mTOR",
    ),
    ChemblTarget(
        gene_symbol="PIK3CA",
        chembl_id="CHEMBL4005",
        preferred_name=(
            "Phosphatidylinositol 4,5-bisphosphate 3-kinase catalytic subunit alpha isoform"
        ),
    ),
    ChemblTarget(
        gene_symbol="ATM", chembl_id="CHEMBL3797", preferred_name="Serine-protein kinase ATM"
    ),
    ChemblTarget(
        gene_symbol="ATR",
        chembl_id="CHEMBL5024",
        preferred_name="Serine/threonine-protein kinase ATR",
    ),
    ChemblTarget(
        gene_symbol="PRKDC",
        chembl_id="CHEMBL3142",
        preferred_name="DNA-dependent protein kinase catalytic subunit",
    ),
]

GENERATIONS = {
    "gen1_rapalogs": DrugGeneration(
        generation_id="gen1_rapalogs",
        title="Generation 1: rapalogs",
        mechanism="Allosteric, FKBP12-dependent inhibitors that bind the FRB domain.",
        limitation="Incomplete 4E-BP1 inhibition and feedback AKT activation.",
        co_receptor="FKBP1A/FKBP12",
        binding_mode=BindingMode.FRB_ALLOSTERIC,
        binding_site="FRB domain cleft adjacent to the kinase active site",
        drug_ids=["sirolimus", "temsirolimus", "everolimus", "ridaforolimus", "zotarolimus"],
    ),
    "gen2_torki": DrugGeneration(
        generation_id="gen2_torki",
        title="Generation 2: TORKi",
        mechanism="ATP-competitive inhibitors of the mTOR kinase active site and mTORC1/2.",
        limitation="Hyperglycemia and GI toxicity; mTORC2-linked metabolic effects.",
        binding_mode=BindingMode.ATP_COMPETITIVE,
        binding_site="ATP pocket in the kinase domain",
        drug_ids=[
            "torin1",
            "torin2",
            "pp242",
            "azd8055",
            "vistusertib",
            "sapanisertib",
            "osi-027",
            "onatasertib",
            "gdc-0349",
        ],
    ),
    "gen2_dual_pi3k_mtor": DrugGeneration(
        generation_id="gen2_dual_pi3k_mtor",
        title="Generation 2: dual PI3K-mTOR",
        mechanism="ATP-competitive inhibitors of PI3K p110 and mTOR.",
        binding_mode=BindingMode.DUAL_PI3K_MTOR_ATP,
        binding_site="Conserved PI3K-family ATP pockets",
        drug_ids=["dactolisib", "gedatolisib", "omipalisib", "voxtalisib"],
    ),
    "gen3_bisteric": DrugGeneration(
        generation_id="gen3_bisteric",
        title="Generation 3: bi-steric",
        mechanism=(
            "Bivalent inhibitors link an FKBP12-rapamycin FRB binder to an ATP-site inhibitor."
        ),
        advantage="Deep mTORC1 inhibition, mTORC2 sparing, and resistance-mutation coverage.",
        co_receptor="FKBP1A/FKBP12",
        binding_mode=BindingMode.BISTERIC_FRB_ATP,
        binding_site="FRB domain and ATP pocket simultaneously",
        drug_ids=["rapalink-1", "rmc-5552", "rmc-6272", "rmc-4627"],
    ),
    "mtorc2_selective": DrugGeneration(
        generation_id="mtorc2_selective",
        title="mTORC2-selective research tool",
        mechanism="Reported disruption of RICTOR-mTOR association.",
        limitation="Specificity is disputed by a 2024 off-target report.",
        binding_mode=BindingMode.RICTOR_MTOR_ASSOCIATION,
        binding_site="RICTOR-mTOR association interface",
        drug_ids=["jr-ab2-011"],
    ),
}


def _drug(
    drug_id: str,
    generation_id: str,
    chembl_id: str,
    *,
    aliases: tuple[str, ...] = (),
    mechanism: str | None = None,
    approvals: tuple[str, ...] = (),
    trials: tuple[str, ...] = (),
    status: str | None = None,
    use: str | None = None,
    off_target: str | None = None,
    doi: str | None = None,
    potency: str | None = None,
    cns_penetrant: bool = False,
    caveat: str | None = None,
) -> DrugRecord:
    """Create one explicit ChEMBL-linked catalog record."""

    generation = GENERATIONS[generation_id]
    refs = [f"chembl:{chembl_id}"]
    if doi:
        refs.append(f"literature:{doi}")
    return DrugRecord(
        drug_id=drug_id,
        name=drug_id,
        generation_id=generation_id,
        chembl_id=chembl_id,
        aliases=list(aliases),
        mechanism=mechanism or generation.mechanism,
        approvals=list(approvals),
        trials=list(trials),
        status=status,
        use=use,
        off_target=off_target,
        doi=doi,
        potency=potency,
        cns_penetrant=cns_penetrant,
        caveat=caveat,
        source_refs=refs,
    )


DRUGS = {
    drug.drug_id: drug
    for drug in [
        _drug(
            "sirolimus",
            "gen1_rapalogs",
            "CHEMBL413",
            aliases=("rapamycin",),
            approvals=("transplant", "LAM"),
        ),
        _drug("temsirolimus", "gen1_rapalogs", "CHEMBL1201182", approvals=("RCC",)),
        _drug(
            "everolimus",
            "gen1_rapalogs",
            "CHEMBL1908360",
            approvals=("RCC", "breast_ER+", "NET", "TSC-SEGA", "TSC-AML", "TSC-seizures"),
        ),
        _drug("ridaforolimus", "gen1_rapalogs", "CHEMBL2103839", status="investigational"),
        _drug("zotarolimus", "gen1_rapalogs", "CHEMBL219410", approvals=("DES_stent",)),
        _drug("torin1", "gen2_torki", "CHEMBL1256459", use="tool"),
        _drug(
            "torin2",
            "gen2_torki",
            "CHEMBL1765602",
            use="tool",
            off_target="ATM/ATR (poor PIKK selectivity)",
        ),
        _drug("pp242", "gen2_torki", "CHEMBL1241674", use="tool"),
        _drug("azd8055", "gen2_torki", "CHEMBL1801204"),
        _drug("vistusertib", "gen2_torki", "CHEMBL2336325", aliases=("AZD2014",)),
        _drug(
            "sapanisertib",
            "gen2_torki",
            "CHEMBL3545097",
            aliases=("MLN0128", "INK128", "TAK-228"),
            trials=("NCT05275673",),
        ),
        _drug("osi-027", "gen2_torki", "CHEMBL3120215"),
        _drug("onatasertib", "gen2_torki", "CHEMBL3586404", aliases=("CC-223",)),
        _drug("gdc-0349", "gen2_torki", "CHEMBL2139930"),
        _drug("dactolisib", "gen2_dual_pi3k_mtor", "CHEMBL1879463", aliases=("BEZ235",)),
        _drug(
            "gedatolisib",
            "gen2_dual_pi3k_mtor",
            "CHEMBL592445",
            aliases=("PKI-587", "PF-05212384"),
        ),
        _drug("omipalisib", "gen2_dual_pi3k_mtor", "CHEMBL1236962", aliases=("GSK2126458",)),
        _drug("voxtalisib", "gen2_dual_pi3k_mtor", "CHEMBL3545366", aliases=("XL765", "SAR245409")),
        _drug(
            "rapalink-1",
            "gen3_bisteric",
            "CHEMBL4303783",
            mechanism="Rapamycin and MLN0128 joined by a 39-atom linker.",
            doi=NATURE_RAPALINK,
            cns_penetrant=True,
        ),
        _drug(
            "rmc-5552",
            "gen3_bisteric",
            "CHEMBL5314926",
            mechanism="Bi-steric mTORC1-selective inhibitor.",
            doi=JMEDCHEM_RMC5552,
            potency=(
                "pS6K IC50 0.14 nM; p4EBP1 IC50 0.48 nM; pAKT IC50 19 nM "
                "(~40x mTORC1/2 selectivity)"
            ),
            trials=("NCT04774952",),
            caveat=(
                "This is mTOR-directed; RMC-6236, RMC-6291, and RMC-9805 are RAS(ON) inhibitors."
            ),
        ),
        _drug(
            "rmc-6272", "gen3_bisteric", "CHEMBL5441038", use="tool bi-steric", doi=JMEDCHEM_RMC5552
        ),
        _drug(
            "rmc-4627", "gen3_bisteric", "CHEMBL5440792", use="tool bi-steric", doi=JMEDCHEM_RMC5552
        ),
        _drug(
            "jr-ab2-011",
            "mtorc2_selective",
            "CHEMBL5274229",
            mechanism="Reported blocker of RICTOR-mTOR association.",
            status="plausible",
            caveat="Specificity is disputed by a 2024 off-target report.",
        ),
    ]
}

STRUCTURAL_SITES = [
    StructuralSite(
        site_id="frb",
        label="FRB allosteric cleft",
        domain="FRB",
        pdb_id="4JSV",
        color="#feca57",
        description="FKBP12-rapamycin-binding domain adjacent to the catalytic cleft.",
    ),
    StructuralSite(
        site_id="atp",
        label="ATP pocket",
        domain="kinase",
        pdb_id="4JT6",
        color="#55c7ff",
        description="Catalytic ATP pocket occupied by ATP-competitive mTOR kinase inhibitors.",
    ),
    StructuralSite(
        site_id="mtorc2",
        label="mTORC2 interface",
        domain="complex interface",
        pdb_id="6ZWM",
        color="#b98cff",
        description="Human mTORC2 model used to contextualize RICTOR-association perturbation.",
    ),
]

RESISTANCE_MUTATIONS = [
    ResistanceMutation(
        mutation_id="A2034V",
        domain="FRB",
        site_id="frb",
        effect="Rapalog resistance at the FRB site.",
        color="#ff6b6b",
        source_refs=[f"literature:{NATURE_RAPALINK}"],
    ),
    ResistanceMutation(
        mutation_id="F2108L",
        domain="FRB",
        site_id="frb",
        effect="Rapalog resistance at the FRB site.",
        color="#ff6b6b",
        source_refs=[f"literature:{NATURE_RAPALINK}"],
    ),
    ResistanceMutation(
        mutation_id="M2327I",
        domain="kinase",
        site_id="atp",
        effect="ATP-competitive inhibitor resistance in the kinase domain.",
        color="#ff6b6b",
        source_refs=[f"literature:{NATURE_RAPALINK}"],
    ),
]


def _normalized_name(name: str) -> str:
    """Normalize display punctuation before alias resolution."""

    return re.sub(r"[^a-z0-9]", "", name.lower())


ALIAS_INDEX = {
    _normalized_name(name): drug
    for drug in DRUGS.values()
    for name in [drug.drug_id, drug.name, *drug.aliases]
}


def drug_by_name(name: str) -> DrugRecord:
    """Resolve one canonical inhibitor record from any registered alias."""

    try:
        return ALIAS_INDEX[_normalized_name(name)]
    except KeyError as error:
        raise KeyError(f"unknown inhibitor alias: {name}") from error


def drug_target_links() -> list[DrugTargetLink]:
    """Return explicit mechanism, tier, and species tags for every drug node."""

    links: list[DrugTargetLink] = []
    for drug in DRUGS.values():
        generation = GENERATIONS[drug.generation_id]
        targets = ["MTOR"]
        tier = Tier.PLAUSIBLE
        species = [SpeciesEvidence.IN_VITRO_BIOCHEMICAL]
        if drug.generation_id == "gen1_rapalogs":
            targets = ["MTORC1"]
            tier = Tier.ROBUST
            species = [SpeciesEvidence.HUMAN, SpeciesEvidence.IN_VITRO_BIOCHEMICAL]
        elif drug.drug_id == "torin1":
            tier = Tier.ROBUST
        elif drug.generation_id == "gen2_dual_pi3k_mtor":
            targets = ["MTOR", "PIK3CA"]
        elif drug.generation_id == "gen3_bisteric":
            targets = ["MTORC1"]
        elif drug.generation_id == "mtorc2_selective":
            targets = ["MTORC2"]
            tier = Tier.SPECULATIVE
        for target in targets:
            links.append(
                DrugTargetLink(
                    drug_id=drug.drug_id,
                    target_node_id=target,
                    mechanism=EdgeMechanism.INHIBITS,
                    binding_mode=generation.binding_mode,
                    tier=tier,
                    species_evidence=species,
                    source_refs=drug.source_refs,
                )
            )
    return links
