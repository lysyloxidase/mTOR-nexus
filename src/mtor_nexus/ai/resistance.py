"""Binding-mode-aware resistance and combination-hypothesis triage."""

from mtor_nexus.ai.models import (
    CombinationSuggestion,
    ResistanceLiability,
    ResistancePrediction,
)
from mtor_nexus.drugs.catalog import RESISTANCE_MUTATIONS
from mtor_nexus.drugs.models import BindingMode, ResistanceMutation

_MUTATIONS = {mutation.mutation_id: mutation for mutation in RESISTANCE_MUTATIONS}
_MODE_LIABILITIES = {
    BindingMode.FRB_ALLOSTERIC: ("A2034V", "F2108L"),
    BindingMode.ATP_COMPETITIVE: ("M2327I",),
    BindingMode.DUAL_PI3K_MTOR_ATP: ("M2327I",),
    BindingMode.BISTERIC_FRB_ATP: ("A2034V", "F2108L", "M2327I"),
    BindingMode.RICTOR_MTOR_ASSOCIATION: (),
}


def _liability(mutation: ResistanceMutation) -> ResistanceLiability:
    """Convert a curated structural mutation into a computational liability."""

    return ResistanceLiability(
        mutation_id=mutation.mutation_id,
        domain=mutation.domain,
        effect=mutation.effect,
    )


class ResistancePredictor:
    """Expose structural liabilities and graph-grounded combination hypotheses."""

    def predict(self, binding_mode: BindingMode) -> ResistancePrediction:
        """Return liabilities for the selected inhibitor binding mode."""

        combinations: list[CombinationSuggestion] = []
        if binding_mode == BindingMode.FRB_ALLOSTERIC:
            combinations.append(
                CombinationSuggestion(
                    partner="AKT inhibitor",
                    rationale=(
                        "Rapalog-like mTORC1 inhibition can relieve feedback control and "
                        "reactivate AKT signaling; prioritize experimental combination testing."
                    ),
                )
            )
        return ResistancePrediction(
            binding_mode=binding_mode,
            liabilities=[
                _liability(_MUTATIONS[mutation]) for mutation in _MODE_LIABILITIES[binding_mode]
            ],
            combinations=combinations,
        )
