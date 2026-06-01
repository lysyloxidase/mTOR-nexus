"""Refresh the RDKit-standardized ChEMBL counter-screen training snapshot."""

import argparse
import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize

from mtor_nexus.drugs.catalog import COUNTER_SCREEN_TARGETS, DRUGS
from mtor_nexus.drugs.models import AssayMetadata, BioactivityRecord, CompoundBioactivity

CHEMBL_API = "https://www.ebi.ac.uk/chembl/api/data"
DEFAULT_SNAPSHOT = "data/curated/chembl-bioactivity.json"
_mol_from_smiles = cast(Callable[[str], Any], Chem.MolFromSmiles)  # pyright: ignore[reportUnknownMemberType]
_cleanup = cast(Callable[[Any], Any], rdMolStandardize.Cleanup)  # pyright: ignore[reportUnknownMemberType]
_fragment_parent = cast(Callable[[Any], Any], rdMolStandardize.FragmentParent)  # pyright: ignore[reportUnknownMemberType]
_mol_to_smiles = cast(Callable[..., str], Chem.MolToSmiles)  # pyright: ignore[reportUnknownMemberType]


def _read_json(url: str) -> dict[str, Any]:
    """Read one public ChEMBL API response."""

    for attempt in range(3):
        try:
            with urlopen(url, timeout=60) as response:  # noqa: S310
                return cast(dict[str, Any], json.load(response))
        except (HTTPError, URLError):
            if attempt == 2:
                raise
            time.sleep(0.6 * (attempt + 1))
    raise AssertionError("unreachable")


def standardize_smiles(smiles: str) -> str:
    """Clean, parent-normalize, and canonically serialize one ChEMBL SMILES."""

    molecule = _mol_from_smiles(smiles)
    if molecule is None:
        raise ValueError("RDKit could not parse ChEMBL canonical SMILES")
    cleaned = _cleanup(molecule)
    parent = _fragment_parent(cleaned)
    return _mol_to_smiles(parent, canonical=True)


def smiles_is_parseable(smiles: str) -> bool:
    """Return whether RDKit accepts one canonicalized SMILES."""

    return _mol_from_smiles(smiles) is not None


def _assay_metadata(
    assay_chembl_id: str,
    fallback_description: str,
    fallback_type: str,
    cache: dict[str, AssayMetadata],
) -> AssayMetadata:
    """Fetch one assay record and reuse it across labels."""

    if assay_chembl_id not in cache:
        try:
            raw = _read_json(f"{CHEMBL_API}/assay/{assay_chembl_id}.json")
            cache[assay_chembl_id] = AssayMetadata(
                assay_chembl_id=assay_chembl_id,
                assay_type=str(raw["assay_type"]),
                description=str(raw["description"]),
                confidence_score=int(raw["confidence_score"]),
            )
        except (HTTPError, URLError):
            cache[assay_chembl_id] = AssayMetadata(
                assay_chembl_id=assay_chembl_id,
                assay_type=fallback_type,
                description=fallback_description,
                confidence_score=0,
            )
    return cache[assay_chembl_id]


def _activity_rows() -> list[dict[str, Any]]:
    """Fetch all catalog labels against the five-target PIKK counter-screen panel."""

    query = urlencode(
        {
            "molecule_chembl_id__in": ",".join(drug.chembl_id for drug in DRUGS.values()),
            "target_chembl_id__in": ",".join(target.chembl_id for target in COUNTER_SCREEN_TARGETS),
            "standard_type__in": "IC50,Ki,Kd",
            "limit": "1000",
        }
    )
    document = _read_json(f"{CHEMBL_API}/activity.json?{query}")
    if document["page_meta"]["next"]:
        raise ValueError("ChEMBL activity snapshot exceeded the configured page size")
    return list(document["activities"])


def refresh_bioactivity_snapshot(path: str = DEFAULT_SNAPSHOT) -> list[CompoundBioactivity]:
    """Pull ChEMBL structures and labels, standardize SMILES, and write the snapshot."""

    assay_cache: dict[str, AssayMetadata] = {}
    drug_by_chembl = {drug.chembl_id: drug for drug in DRUGS.values()}
    target_by_chembl = {target.chembl_id: target for target in COUNTER_SCREEN_TARGETS}
    rows_by_drug: dict[str, list[BioactivityRecord]] = {drug_id: [] for drug_id in DRUGS}
    for raw in _activity_rows():
        if (
            raw["standard_value"] is None
            or raw["standard_units"] is None
            or raw["standard_relation"] is None
        ):
            continue
        drug = drug_by_chembl[str(raw["molecule_chembl_id"])]
        target = target_by_chembl[str(raw["target_chembl_id"])]
        assay_chembl_id = str(raw["assay_chembl_id"])
        rows_by_drug[drug.drug_id].append(
            BioactivityRecord(
                activity_id=int(raw["activity_id"]),
                drug_id=drug.drug_id,
                molecule_chembl_id=drug.chembl_id,
                target_gene_symbol=target.gene_symbol,
                target_chembl_id=target.chembl_id,
                standard_type=str(raw["standard_type"]),
                standard_relation=str(raw["standard_relation"]),
                standard_value=float(raw["standard_value"]),
                standard_units=str(raw["standard_units"]),
                assay=_assay_metadata(
                    assay_chembl_id,
                    str(raw["assay_description"]),
                    str(raw["assay_type"]),
                    assay_cache,
                ),
            )
        )
    compounds: list[CompoundBioactivity] = []
    for drug in DRUGS.values():
        molecule = _read_json(f"{CHEMBL_API}/molecule/{drug.chembl_id}.json")
        canonical_smiles = str(molecule["molecule_structures"]["canonical_smiles"])
        compounds.append(
            CompoundBioactivity(
                drug_id=drug.drug_id,
                molecule_chembl_id=drug.chembl_id,
                canonical_smiles=canonical_smiles,
                rdkit_standardized_smiles=standardize_smiles(canonical_smiles),
                activities=sorted(rows_by_drug[drug.drug_id], key=lambda row: row.activity_id),
            )
        )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            [compound.model_dump(mode="json") for compound in compounds], indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    return compounds


def load_bioactivity_snapshot(path: str = DEFAULT_SNAPSHOT) -> list[CompoundBioactivity]:
    """Load the committed derived ChEMBL training snapshot."""

    return [
        CompoundBioactivity.model_validate(record)
        for record in json.loads(Path(path).read_text(encoding="utf-8"))
    ]


def main() -> int:
    """Refresh the public ChEMBL-derived bioactivity snapshot."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=DEFAULT_SNAPSHOT)
    args = parser.parse_args()
    compounds = refresh_bioactivity_snapshot(args.output)
    print(f"refreshed {len(compounds)} compounds")
    print(f"retained {sum(len(compound.activities) for compound in compounds)} bioactivity labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
