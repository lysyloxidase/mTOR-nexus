"""Helpers for source snapshot provenance records."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def sha256_file(path: str) -> str:
    """Calculate a streaming SHA-256 digest."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as source_file:
        for block in iter(lambda: source_file.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def build_provenance_record(source: str, version: str, path: str) -> dict[str, str]:
    """Build a FAIR provenance record for a downloaded source snapshot."""

    return {
        "source": source,
        "version": version,
        "path": path,
        "sha256": sha256_file(path),
        "timestamp": datetime.now(UTC).isoformat(),
    }


def append_provenance(record: dict[str, str], ledger: str = "data/provenance.jsonl") -> None:
    """Append a record to the JSON Lines provenance ledger."""

    with Path(ledger).open("a", encoding="utf-8") as ledger_file:
        ledger_file.write(json.dumps(record, sort_keys=True) + "\n")
