"""Boltz-2 cofolding handoff for structural triage.

The repository does not bundle Boltz weights or claim an affinity score. This
module prepares a reproducible input template and keeps wet-lab validation
mandatory for every future pose.
"""

from mtor_nexus.ai.models import CofoldingTriageResult, PredictionStatus, RefusalReason
from mtor_nexus.drugs.bioactivity import standardize_smiles


class CofoldingTriage:
    """Prepare an external Boltz-2 run without fabricating a pose or affinity."""

    receptor = "human MTOR kinase-domain construct"

    def prepare(self, smiles: str) -> CofoldingTriageResult:
        """Standardize a ligand and emit the reviewed-sequence handoff template."""

        try:
            standardized = standardize_smiles(smiles)
        except ValueError:
            return CofoldingTriageResult(
                status=PredictionStatus.REFUSED,
                standardized_smiles=None,
                receptor=self.receptor,
                refusal_reason=RefusalReason.INVALID_SMILES,
                message="invalid SMILES - Boltz-2 handoff was not prepared",
                boltz_yaml_template=None,
            )
        template = f"""version: 1
sequences:
  - protein:
      id: A
      sequence: PASTE_REVIEWED_HUMAN_MTOR_CONSTRUCT_SEQUENCE_HERE
  - ligand:
      id: B
      smiles: "{standardized}"
properties:
  - affinity:
      binder: B
"""
        return CofoldingTriageResult(
            status=PredictionStatus.PREPARED,
            standardized_smiles=standardized,
            receptor=self.receptor,
            refusal_reason=RefusalReason.COFOLDING_NOT_CONFIGURED,
            message=(
                "Boltz-2 input prepared only - review the receptor construct and run the "
                "external model before structural triage"
            ),
            boltz_yaml_template=template,
        )
