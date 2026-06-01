"""Write deterministic public pharmacology exports."""

import json
from pathlib import Path
from typing import Any

from mtor_nexus.drugs.bioactivity import load_bioactivity_snapshot
from mtor_nexus.drugs.catalog import (
    COUNTER_SCREEN_TARGETS,
    DRUGS,
    GENERATIONS,
    RESISTANCE_MUTATIONS,
    STRUCTURAL_SITES,
    drug_target_links,
)
from mtor_nexus.drugs.models import DrugDocument

DEFAULT_PROCESSED_PATH = "data/processed/drug-layer.json"
DEFAULT_WEB_PATH = "webapp/public/data/drugs.json"


def drug_document() -> dict[str, Any]:
    """Serialize the inhibitor layer and its Phase 6 training labels."""

    document = DrugDocument(
        schema_version="0.5.0",
        metadata={
            "title": "mTOR-NEXUS Phase 5 drug-discovery layer",
            "chembl_snapshot": "public-api-derived",
            "smiles_standardization": "RDKit Cleanup + FragmentParent + canonical SMILES",
            "training_set_for": "Phase 6 selectivity model",
            "report_identifier_corrections_applied": True,
        },
        generations=list(GENERATIONS.values()),
        drugs=list(DRUGS.values()),
        target_links=drug_target_links(),
        structural_sites=STRUCTURAL_SITES,
        resistance_mutations=RESISTANCE_MUTATIONS,
        counter_screen_targets=COUNTER_SCREEN_TARGETS,
        bioactivity=load_bioactivity_snapshot(),
    )
    return document.model_dump(mode="json")


def write_drug_exports(
    processed_path: str = DEFAULT_PROCESSED_PATH,
    web_path: str = DEFAULT_WEB_PATH,
) -> None:
    """Write normalized and browser-ready inhibitor documents."""

    document = drug_document()
    for path in [processed_path, web_path]:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
