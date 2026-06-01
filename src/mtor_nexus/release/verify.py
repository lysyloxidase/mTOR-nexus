"""Verify deterministic artifacts available to an independent reproduction image."""

import argparse
import json
from pathlib import Path
from typing import Any, cast

from mtor_nexus.release.figures import figure_checksums_match, figure_exports_reproduce
from mtor_nexus.release.readiness import publication_readiness
from mtor_nexus.utils.reproducibility import sha256_file


def export_manifest_matches(path: str = "data/processed/export-manifest.json") -> bool:
    """Verify every normalized exchange artifact against the committed manifest."""

    root = Path(path).parent
    document = cast(dict[str, Any], json.loads(Path(path).read_text(encoding="utf-8")))
    artifacts = cast(dict[str, str], document["artifacts"])
    return all(
        (root / relative).is_file() and sha256_file(str(root / relative)) == digest
        for relative, digest in artifacts.items()
    )


def independent_reproduction_report(
    *,
    allow_pending_independent_reproduction: bool = False,
    allow_pending_zenodo_doi: bool = False,
) -> dict[str, Any]:
    """Return local reproduction checks and the separate publication gate state."""

    readiness = publication_readiness(
        allow_pending_independent_reproduction=allow_pending_independent_reproduction,
        allow_pending_zenodo_doi=allow_pending_zenodo_doi,
    )
    return {
        "schema_version": "0.7.0",
        "export_manifest_matches": export_manifest_matches(),
        "figure_checksums_match": figure_checksums_match(),
        "figure_exports_reproduce": figure_exports_reproduce(),
        "production_release_ready": readiness["production_release_ready"],
        "required_release_gates_passed": readiness["required_gates_passed"],
        "release_blocking_reasons": readiness["blocking_reasons"],
        "release_deferred_reasons": readiness["deferred_reasons"],
    }


def main() -> int:
    """Verify deterministic bytes; optionally fail until production gates pass."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--require-production", action="store_true")
    parser.add_argument("--allow-pending-independent-reproduction", action="store_true")
    parser.add_argument("--allow-pending-zenodo-doi", action="store_true")
    args = parser.parse_args()
    report = independent_reproduction_report(
        allow_pending_independent_reproduction=args.allow_pending_independent_reproduction,
        allow_pending_zenodo_doi=args.allow_pending_zenodo_doi,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    deterministic_passed = (
        report["export_manifest_matches"]
        and report["figure_checksums_match"]
        and report["figure_exports_reproduce"]
    )
    production_passed = report["required_release_gates_passed"] or not args.require_production
    return int(not deterministic_passed or not production_passed)


if __name__ == "__main__":
    raise SystemExit(main())
