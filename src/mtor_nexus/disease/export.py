"""Write deterministic disease-layer exports for analysis and browser overlays."""

import json
from pathlib import Path
from typing import Any

from mtor_nexus.disease.classes import DISEASE_CLASSES, disease_associations
from mtor_nexus.disease.mutations import curated_mutations

DEFAULT_PROCESSED_PATH = "data/processed/disease-layer.json"
DEFAULT_WEB_PATH = "webapp/public/data/diseases.json"


def disease_document() -> dict[str, Any]:
    """Serialize the public disease overlay without restricted COSMIC records."""

    return {
        "schema_version": "0.4.0",
        "metadata": {
            "title": "mTOR-NEXUS Phase 4 disease layer",
            "cosmic_raw_redistributed": False,
            "cosmic_handling": "licensed-local-reconciliation-overlay-only",
            "cbioportal_frequency_note": (
                "PIK3CA ER-positive breast frequency is a live-source-derived mutation-only "
                "reference, not a pan-alteration prevalence estimate."
            ),
        },
        "disease_classes": [
            disease.model_dump(mode="json") for disease in DISEASE_CLASSES.values()
        ],
        "associations": [
            association.model_dump(mode="json") for association in disease_associations()
        ],
        "mutations": [mutation.model_dump(mode="json") for mutation in curated_mutations()],
    }


def write_disease_exports(
    processed_path: str = DEFAULT_PROCESSED_PATH,
    web_path: str = DEFAULT_WEB_PATH,
) -> None:
    """Write the normalized and browser-ready disease-layer documents."""

    document = disease_document()
    for path in [processed_path, web_path]:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
