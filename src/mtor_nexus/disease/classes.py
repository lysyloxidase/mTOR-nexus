"""Eight evidence-aware disease classes mapped onto the mTOR pathway."""

from mtor_nexus.disease.models import (
    ApprovedDrug,
    CohortFrequency,
    DiseaseAssociation,
    DiseaseClass,
    PerturbationDirection,
    RareSyndrome,
    TrialLink,
)
from mtor_nexus.schema import SpeciesEvidence, Tier

FDA_AFINITOR = (
    "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=022334"
)
FDA_RAPAMUNE = (
    "https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=021083"
)
CBIOPORTAL_ER_POSITIVE_PIK3CA = CohortFrequency(
    gene_symbol="PIK3CA",
    cohort="TCGA Firehose Legacy breast cancer, ER_STATUS_BY_IHC=Positive",
    altered_cases=271,
    profiled_cases=808,
    frequency_percent=33.539603960396036,
    source_url="https://www.cbioportal.org/study/summary?id=brca_tcga",
)

RARE_SYNDROMES = [
    RareSyndrome(
        syndrome_id="TSC",
        genes=["TSC1", "TSC2"],
        drug="everolimus (FDA: SEGA, renal AML, and TSC-associated seizures)",
    ),
    RareSyndrome(
        syndrome_id="LAM",
        genes=["TSC1", "TSC2"],
        drug="sirolimus (FDA; MILES trial evidence)",
    ),
    RareSyndrome(
        syndrome_id="PMSE_Pretzel",
        genes=["STRADA"],
        inheritance="recessive",
        drug="rapamycin investigated for seizure prevention",
    ),
    RareSyndrome(
        syndrome_id="Smith_Kingsmore",
        genes=["MTOR"],
        recurrent_variant="p.Glu1799Lys",
        omim="616638",
    ),
    RareSyndrome(syndrome_id="Cowden", genes=["PTEN"]),
    RareSyndrome(syndrome_id="Peutz_Jeghers", genes=["STK11"]),
]

DISEASE_CLASSES = {
    disease.disease_id: disease
    for disease in [
        DiseaseClass(
            disease_id="cancer",
            title="Cancer",
            key_nodes=["PIK3CA", "PTEN", "TSC1", "TSC2", "AKT1", "RHEB", "STK11", "MTOR"],
            indications=[
                "breast_ER+",
                "RCC",
                "endometrial",
                "NSCLC",
                "pancreatic",
                "glioblastoma",
                "lymphoma",
            ],
            mechanism="Oncogenic activation and suppressor loss converge on mTORC1 signaling.",
            tier=Tier.ROBUST,
            species_evidence=[SpeciesEvidence.HUMAN],
            cohort_frequencies=[CBIOPORTAL_ER_POSITIVE_PIK3CA],
            source_refs=["cbioportal:brca_tcga", "cosmic:restricted-local-overlay"],
        ),
        DiseaseClass(
            disease_id="mtoropathies_epilepsy",
            title="mTORopathies and epilepsy",
            key_nodes=["DEPDC5", "TSC1", "TSC2", "MTOR", "NPRL2", "NPRL3"],
            diseases=["FCD_type_II", "familial_focal_epilepsy", "hemimegalencephaly", "TSC"],
            mechanism="Two-hit germline and somatic DEPDC5 loss; mosaic MTOR activation.",
            tier=Tier.ROBUST,
            species_evidence=[SpeciesEvidence.HUMAN],
            source_refs=["clinvar:gene-overlay", "clinvar:VCV000217823.74"],
        ),
        DiseaseClass(
            disease_id="neurodegeneration",
            title="Neurodegeneration",
            key_nodes=["MTOR", "ULK1", "TFEB", "BECN1"],
            diseases=["Alzheimer", "Parkinson", "Huntington", "ALS_FTD"],
            mechanism="Autophagy impairment with temporal dependence of rapamycin response.",
            tier=Tier.PLAUSIBLE,
            species_evidence=[SpeciesEvidence.RODENT],
            species_caveat="Rapamycin benefit is strongest before pathology in disease models.",
            source_refs=["curated:neurodegeneration-autophagy"],
        ),
        DiseaseClass(
            disease_id="aging_longevity",
            title="Aging and longevity",
            key_nodes=["MTOR", "RPTOR", "RPS6KB1"],
            mechanism="Reduced nutrient signaling is associated with rodent lifespan extension.",
            tier=Tier.ROBUST,
            species_evidence=[SpeciesEvidence.RODENT, SpeciesEvidence.HUMAN],
            species_caveat=(
                "RODENT for lifespan; HUMAN evidence remains early and limited for healthspan."
            ),
            source_refs=["curated:itp-lifespan", "curated:pearl-healthspan"],
        ),
        DiseaseClass(
            disease_id="metabolic",
            title="Metabolic disease",
            key_nodes=["RPS6KB1", "RICTOR", "IRS1", "SREBF1", "AKT2"],
            diseases=["T2D", "obesity", "NAFLD_NASH", "insulin_resistance"],
            mechanism="S6K1 feedback and mTORC2-AKT2 perturbation alter metabolic homeostasis.",
            tier=Tier.ROBUST,
            species_evidence=[SpeciesEvidence.RODENT],
            species_caveat=(
                "MOSTLY RODENT models; translation to human metabolic disease remains qualified."
            ),
            source_refs=["curated:s6k1-knockout", "curated:liriko"],
        ),
        DiseaseClass(
            disease_id="rare_syndromes",
            title="Rare syndromes",
            key_nodes=["TSC1", "TSC2", "STRADA", "MTOR", "PTEN", "STK11"],
            mechanism="Germline pathway disruption creates syndrome-specific mTOR dysregulation.",
            tier=Tier.ROBUST,
            species_evidence=[SpeciesEvidence.HUMAN],
            rare_syndromes=RARE_SYNDROMES,
            approved_drugs=[
                ApprovedDrug(
                    name="everolimus",
                    indication="TSC-associated SEGA, renal AML, and seizures",
                    status="FDA-approved",
                    source_url=FDA_AFINITOR,
                ),
                ApprovedDrug(
                    name="sirolimus",
                    indication="lymphangioleiomyomatosis",
                    status="FDA-approved",
                    source_url=FDA_RAPAMUNE,
                ),
            ],
            trial_links=[
                TrialLink(
                    nct_id="NCT01289912",
                    title="Trial of RAD001 and neurocognition in tuberous sclerosis complex",
                    url="https://clinicaltrials.gov/study/NCT01289912",
                ),
                TrialLink(
                    nct_id="NCT03253913",
                    title="Resveratrol and sirolimus in lymphangioleiomyomatosis trial",
                    url="https://clinicaltrials.gov/study/NCT03253913",
                ),
            ],
            source_refs=["clinvar:gene-overlay", "fda:022334", "fda:021083"],
        ),
        DiseaseClass(
            disease_id="immunology_transplant",
            title="Immunology and transplant",
            key_nodes=["MTOR", "RPTOR", "RICTOR"],
            mechanism="mTOR balances Th1/Th17 versus Treg and effector versus memory CD8 states.",
            tier=Tier.ROBUST,
            species_evidence=[SpeciesEvidence.HUMAN_AND_RODENT],
            approved_drugs=[
                ApprovedDrug(
                    name="sirolimus",
                    indication="transplant immunosuppression",
                    status="FDA-approved",
                    source_url=FDA_RAPAMUNE,
                )
            ],
            source_refs=["curated:immunology-transplant", "fda:021083"],
        ),
        DiseaseClass(
            disease_id="cardiovascular",
            title="Cardiovascular disease",
            key_nodes=["MTOR", "RPS6KB1"],
            diseases=["cardiac_hypertrophy", "atherosclerosis", "restenosis"],
            mechanism="mTORC1-S6K1 activity contributes to remodeling and restenosis.",
            tier=Tier.ROBUST,
            species_evidence=[SpeciesEvidence.HUMAN_AND_RODENT],
            source_refs=["curated:cardiovascular-stents"],
        ),
    ]
}

PERTURBATIONS = {
    "PIK3CA": PerturbationDirection.HYPERACTIVATION,
    "PTEN": PerturbationDirection.LOSS,
    "TSC1": PerturbationDirection.LOSS,
    "TSC2": PerturbationDirection.LOSS,
    "AKT1": PerturbationDirection.HYPERACTIVATION,
    "RHEB": PerturbationDirection.HYPERACTIVATION,
    "STK11": PerturbationDirection.LOSS,
    "MTOR": PerturbationDirection.HYPERACTIVATION,
    "DEPDC5": PerturbationDirection.LOSS,
    "NPRL2": PerturbationDirection.LOSS,
    "NPRL3": PerturbationDirection.LOSS,
    "ULK1": PerturbationDirection.LOSS,
    "TFEB": PerturbationDirection.LOSS,
    "BECN1": PerturbationDirection.LOSS,
    "RPTOR": PerturbationDirection.MIXED,
    "RPS6KB1": PerturbationDirection.HYPERACTIVATION,
    "RICTOR": PerturbationDirection.LOSS,
    "IRS1": PerturbationDirection.LOSS,
    "SREBF1": PerturbationDirection.HYPERACTIVATION,
    "AKT2": PerturbationDirection.LOSS,
    "STRADA": PerturbationDirection.LOSS,
}


def disease_associations() -> list[DiseaseAssociation]:
    """Expand disease classes into evidence-bearing disease-to-node edges."""

    return [
        DiseaseAssociation(
            disease_id=disease.disease_id,
            pathway_node_id=node_id,
            perturbation=PERTURBATIONS.get(node_id, PerturbationDirection.UNCERTAIN),
            tier=disease.tier,
            species_evidence=disease.species_evidence,
            source_refs=disease.source_refs,
        )
        for disease in DISEASE_CLASSES.values()
        for node_id in disease.key_nodes
    ]
