# pyright: reportMissingTypeStubs=false, reportUnknownArgumentType=false, reportUnknownMemberType=false
"""Computational-only scaffold enumeration with lightweight developability filters.

This prerelease does not claim a trained molecular generator. It exposes a
small deterministic scaffold-exploration surface so the validation policy and
future selectivity scorer can be exercised end to end.
"""

from collections.abc import Callable
from typing import Any, cast

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

from mtor_nexus.ai.models import ScaffoldCandidate
from mtor_nexus.ai.selectivity_gnn import SelectivityGNN
from mtor_nexus.drugs.bioactivity import standardize_smiles

_mol_from_smiles = cast(Callable[[str], Any], Chem.MolFromSmiles)  # pyright: ignore[reportUnknownMemberType]
_molecular_weight = cast(Callable[[Any], float], Descriptors.MolWt)  # pyright: ignore[reportAttributeAccessIssue]
_logp = cast(Callable[[Any], float], Descriptors.MolLogP)  # pyright: ignore[reportAttributeAccessIssue]
_SCAFFOLDS = [
    ("exploratory-kinase-001", "CCOc1ccc(Nc2ncnc3cc(OC)c(OC)cc23)cc1"),
    ("exploratory-kinase-002", "O=C(Nc1ccc(F)cc1)c1ccnc(N2CCOCC2)n1"),
    ("exploratory-allosteric-003", "CC1(C)CC(c2ccc(OCCN3CCOCC3)cc2)CC(C)(C)O1"),
]


def _developability(smiles: str) -> tuple[float, bool, list[str]]:
    """Calculate transparent heuristics; these are triage filters, not ADMET models."""

    molecule = _mol_from_smiles(smiles)
    if molecule is None:
        raise ValueError("internal scaffold SMILES is invalid")
    molecular_weight = _molecular_weight(molecule)
    logp = _logp(molecule)
    hydrogen_bond_donors = int(rdMolDescriptors.CalcNumHBD(molecule))
    hydrogen_bond_acceptors = int(rdMolDescriptors.CalcNumHBA(molecule))
    rotatable_bonds = int(rdMolDescriptors.CalcNumRotatableBonds(molecule))
    rings = int(rdMolDescriptors.CalcNumRings(molecule))
    proxy = min(10.0, max(1.0, 1.0 + rotatable_bonds * 0.35 + rings * 0.25))
    notes = [
        f"MW={molecular_weight:.1f}",
        f"cLogP={logp:.2f}",
        f"HBD={hydrogen_bond_donors}",
        f"HBA={hydrogen_bond_acceptors}",
        f"rotatable_bonds={rotatable_bonds}",
        "heuristic filter only - not an ADMET prediction",
    ]
    passed = (
        molecular_weight <= 550
        and logp <= 5
        and hydrogen_bond_donors <= 5
        and hydrogen_bond_acceptors <= 10
    )
    return proxy, passed, notes


class ScaffoldExplorer:
    """Enumerate red-tagged hypotheses and route them through refusal-bound scoring."""

    def __init__(self, selectivity: SelectivityGNN | None = None) -> None:
        """Reuse the selectivity shell so no candidate bypasses the AD gate."""

        self.selectivity = selectivity or SelectivityGNN()

    def generate(self, limit: int = 3) -> list[ScaffoldCandidate]:
        """Return deterministic, computational-only exploratory scaffolds."""

        candidates: list[ScaffoldCandidate] = []
        for scaffold_id, smiles in _SCAFFOLDS[: max(0, limit)]:
            standardized = standardize_smiles(smiles)
            proxy, passed, notes = _developability(standardized)
            candidates.append(
                ScaffoldCandidate(
                    scaffold_id=scaffold_id,
                    smiles=standardized,
                    synthetic_accessibility_proxy=proxy,
                    admet_filter_passed=passed,
                    admet_notes=notes,
                    selectivity=self.selectivity.predict(standardized),
                )
            )
        return candidates
