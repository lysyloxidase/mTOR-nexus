"""Export browser and analysis readiness documents for the AI prerelease."""

import json
from pathlib import Path

from mtor_nexus.ai.service import ai_status_document


def write_ai_exports(
    processed_path: str = "data/processed/ai-engine-status.json",
    web_path: str = "webapp/public/data/ai-status.json",
) -> None:
    """Write the same machine-readable readiness report for analysis and UI."""

    document = ai_status_document()
    for raw_path in [processed_path, web_path]:
        path = Path(raw_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
