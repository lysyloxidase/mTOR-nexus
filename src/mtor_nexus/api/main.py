"""API surface for health checks, pathway retrieval, and overlay documents."""

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mtor_nexus import __version__
from mtor_nexus.ai.models import PredictionBundle, PredictionRequest, ScaffoldCandidate
from mtor_nexus.ai.service import AIEngine, ai_status_document
from mtor_nexus.config.settings import settings

app = FastAPI(title="mTOR-NEXUS API", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
ai_engine = AIEngine()


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


@app.get("/ai/status")
def ai_status() -> dict[str, Any]:
    """Return measured readiness and locked selectivity-model gates."""

    return ai_status_document()


@app.post("/ai/predict")
def ai_predict(request: PredictionRequest) -> PredictionBundle:
    """Run refusal-bound selectivity, resistance, and optional cofolding triage."""

    return ai_engine.predict(request)


@app.get("/ai/scaffolds")
def ai_scaffolds(limit: int = 3) -> list[ScaffoldCandidate]:
    """Return red-tagged computational-only scaffold hypotheses."""

    return ai_engine.generate_scaffolds(limit=min(10, max(0, limit)))
