"""Load a licensed local COSMIC reconciliation overlay without redistribution."""

import csv
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class CosmicOverlayRecord(BaseModel):
    """Minimal local COSMIC mapping retained only during licensed workflows."""

    model_config = ConfigDict(extra="forbid")

    cosmic_id: str = Field(pattern=r"^COS[MV]\d+$")
    gene_symbol: str = Field(min_length=1)
    hgvs_protein: str = Field(min_length=1)


def load_cosmic_overlay(path: str) -> list[CosmicOverlayRecord]:
    """Read a curator-provided restricted TSV snapshot."""

    with Path(path).open(encoding="utf-8", newline="") as overlay_file:
        return [
            CosmicOverlayRecord(
                cosmic_id=row["COSMIC_ID"],
                gene_symbol=row["GENE_SYMBOL"],
                hgvs_protein=row["HGVSP"],
            )
            for row in csv.DictReader(overlay_file, delimiter="\t")
        ]
