"""API surface for health checks, pathway retrieval, and overlay documents."""

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from mtor_nexus import __version__
from mtor_nexus.config.settings import settings

app = FastAPI(title="mTOR-NEXUS API", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    """Report service readiness."""

    return {"status": "ok", "version": __version__}


@app.get("/graph")
def graph() -> dict[str, Any]:
    """Return the normalized pathway graph."""

    with Path(settings.graph_path).open(encoding="utf-8") as graph_file:
        return json.load(graph_file)


@app.get("/diseases")
def diseases() -> dict[str, Any]:
    """Return the normalized disease and mutation overlay."""

    with Path(settings.disease_path).open(encoding="utf-8") as disease_file:
        return json.load(disease_file)


@app.get("/drugs")
def drugs() -> dict[str, Any]:
    """Return the normalized inhibitor pharmacology and bioactivity layer."""

    with Path(settings.drug_path).open(encoding="utf-8") as drug_file:
        return json.load(drug_file)
