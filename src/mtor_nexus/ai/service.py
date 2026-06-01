"""Orchestration layer for the Phase 6 AI prerelease."""

from typing import Any

from mtor_nexus.ai.cofolding import CofoldingTriage
from mtor_nexus.ai.generative import ScaffoldExplorer
from mtor_nexus.ai.models import PredictionBundle, PredictionRequest, ScaffoldCandidate
from mtor_nexus.ai.resistance import ResistancePredictor
from mtor_nexus.ai.selectivity_gnn import (
    SelectivityGNN,
    architecture_contract,
    training_data_audit,
)


class AIEngine:
    """Join honest model-readiness, triage, and hypothesis-generation surfaces."""

    def __init__(self) -> None:
        """Load deterministic local services once for API reuse."""

        self.selectivity = SelectivityGNN()
        self.cofolding = CofoldingTriage()
        self.resistance = ResistancePredictor()
        self.scaffolds = ScaffoldExplorer(self.selectivity)

    def predict(self, request: PredictionRequest) -> PredictionBundle:
        """Return a combined prediction bundle without unsupported numbers."""

        return PredictionBundle(
            selectivity=self.selectivity.predict(request.smiles),
            resistance=self.resistance.predict(request.binding_mode),
            cofolding=self.cofolding.prepare(request.smiles) if request.include_cofolding else None,
        )

    def generate_scaffolds(self, limit: int = 3) -> list[ScaffoldCandidate]:
        """Enumerate red-tagged scaffold hypotheses."""

        return self.scaffolds.generate(limit)


def ai_status_document() -> dict[str, Any]:
    """Serialize current model readiness and prerelease policy."""

    return {
        "schema_version": "0.6.0",
        "release": "phase6-prerelease",
        "scientific_release_ready": False,
        "selectivity_gnn": training_data_audit().model_dump(mode="json"),
        "architecture_contract": architecture_contract().model_dump(mode="json"),
        "cofolding": {
            "implementation": "external-boltz-2-handoff",
            "weights_bundled": False,
            "required_experimental_validation": True,
        },
        "resistance": {
            "implementation": "curated-binding-mode-liability-triage",
            "required_experimental_validation": True,
        },
        "scaffold_explorer": {
            "implementation": "deterministic-heuristic-enumeration",
            "trained_generator": False,
            "required_experimental_validation": True,
            "tag": "red_computational_only_unvalidated",
        },
    }
