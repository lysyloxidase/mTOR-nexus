"""Machine-readable, fail-closed publication readiness audit."""

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from mtor_nexus.release.figures import figure_exports_reproduce

DEFAULT_OUTPUT = "data/release/publication-readiness.json"
BIO_RXIV_DOI = re.compile(r"10\.1101/\d{4}\.\d{2}\.\d{2}\.\d+")
ORCID = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class ReleaseGate:
    """One auditable publication-release prerequisite."""

    name: str
    passed: bool
    detail: str


def _read_json(path: str) -> dict[str, Any]:
    """Read a JSON object from disk."""

    return cast(dict[str, Any], json.loads(Path(path).read_text(encoding="utf-8")))


def _citation_document() -> dict[str, Any]:
    """Read structured citation metadata."""

    return cast(dict[str, Any], yaml.safe_load(Path("CITATION.cff").read_text(encoding="utf-8")))


def _ai_gate() -> ReleaseGate:
    """Require a genuinely validated numerical selectivity artifact."""

    status = _read_json("data/processed/ai-engine-status.json")
    selectivity = cast(dict[str, Any], status["selectivity_gnn"])
    passed = (
        status["scientific_release_ready"] is True
        and selectivity["release_status"] == "validated"
        and selectivity["torin2_benchmark_passed"] is True
        and selectivity["deterministic_weights_passed"] is True
        and selectivity["a100_no_oom_tested"] is True
    )
    return ReleaseGate(
        "validated_selectivity_model",
        passed,
        "Torin2, deterministic-weight, and A100 gates must all be measured and true",
    )


def _file_gate(name: str, paths: list[str], detail: str) -> ReleaseGate:
    """Require every path in a release-artifact group."""

    missing = [path for path in paths if not Path(path).is_file()]
    return ReleaseGate(
        name, not missing, detail if not missing else f"missing: {', '.join(missing)}"
    )


def _independent_reproduction_gate() -> ReleaseGate:
    """Require a structured attestation emitted by the clean-runner workflow."""

    path = Path("data/release/independent-reproduction-passed.json")
    if not path.is_file():
        return ReleaseGate(
            "independent_reproduction",
            False,
            "a clean-runner Docker-image reproduction attestation has not been recorded",
        )
    attestation = _read_json(str(path))
    passed = (
        attestation.get("status") == "passed"
        and attestation.get("recorded_by") == "github-actions-independent-reproduction"
        and isinstance(attestation.get("image"), str)
        and attestation["image"].startswith("ghcr.io/")
        and isinstance(attestation.get("commit_sha"), str)
        and COMMIT_SHA.fullmatch(attestation["commit_sha"]) is not None
        and isinstance(attestation.get("github_run_id"), str)
        and attestation["github_run_id"].isdigit()
        and isinstance(attestation.get("run_url"), str)
        and attestation["run_url"].startswith("https://github.com/")
    )
    return ReleaseGate(
        "independent_reproduction",
        passed,
        "clean-runner attestation must identify the GHCR image, commit, and GitHub Actions run",
    )


def publication_readiness(
    *,
    allow_pending_independent_reproduction: bool = False,
    allow_pending_zenodo_doi: bool = False,
) -> dict[str, Any]:
    """Return every local and external blocker for a production v1.0.0 release."""

    citation = _citation_document()
    authors = cast(list[dict[str, Any]], citation.get("authors", []))
    readme = Path("README.md").read_text(encoding="utf-8")
    checklist = Path("docs/submission-checklist.md").read_text(encoding="utf-8")
    lighthouse = _read_json("webapp/lighthouserc.json")
    lighthouse_urls = cast(list[str], lighthouse["ci"]["collect"]["url"])
    assertions = cast(dict[str, Any], lighthouse["ci"]["assert"]["assertions"])
    expected_urls = {
        "http://localhost:3000/",
        "http://localhost:3000/graph",
        "http://localhost:3000/module/1",
        "http://localhost:3000/disease/cancer",
        "http://localhost:3000/drug/sirolimus",
        "http://localhost:3000/node/MTOR",
        "http://localhost:3000/predict",
    }
    zenodo_doi = ReleaseGate(
        "zenodo_doi",
        isinstance(citation.get("doi"), str)
        and citation["doi"].startswith("10.5281/zenodo.")
        and "zenodo.org/badge/DOI/" in readme,
        "production Zenodo DOI and README badge are absent until publish succeeds",
    )
    independent_reproduction = _independent_reproduction_gate()
    gates = [
        _ai_gate(),
        _file_gate(
            "model_weights",
            ["data/models/selectivity-gnn-v1.0.pt"],
            "validated selectivity weights are staged",
        ),
        _file_gate(
            "release_pdfs",
            [
                "docs/release-pdfs/ai-model-cards.pdf",
                "docs/release-pdfs/selectivity-datasheet.pdf",
                "docs/release-pdfs/caveats.pdf",
            ],
            "model cards, datasheet, and caveats PDFs are staged",
        ),
        ReleaseGate(
            "deterministic_figures",
            figure_exports_reproduce(),
            "seven module SVGs, one Python-generated README chart, provenance, checksums, "
            "and regenerated bytes must match",
        ),
        ReleaseGate(
            "author_orcids",
            bool(authors)
            and all(
                isinstance(author.get("orcid"), str) and ORCID.fullmatch(author["orcid"])
                for author in authors
            ),
            "every author in CITATION.cff must include a valid ORCID",
        ),
        zenodo_doi,
        ReleaseGate(
            "biorxiv_preprint",
            BIO_RXIV_DOI.search(Path("docs/preprint-status.md").read_text(encoding="utf-8"))
            is not None,
            "bioRxiv DOI is pending author submission and screening",
        ),
        ReleaseGate(
            "research_report_caveats",
            "Research Report was not included"
            not in Path("docs/caveats.md").read_text(encoding="utf-8"),
            "the complete source Research Report caveat section has not been supplied",
        ),
        ReleaseGate(
            "nomenclature_guards",
            all(
                token in Path("src/mtor_nexus/utils/nomenclature.py").read_text(encoding="utf-8")
                for token in ["RMC-6236", "S2448", "S1462", "S2481", "SAPANISERTIB"]
            ),
            "five hard nomenclature guards are encoded in CI-tested Python",
        ),
        ReleaseGate(
            "lighthouse_route_families",
            set(lighthouse_urls) == expected_urls
            and assertions["categories:performance"][0] == "error"
            and assertions["categories:accessibility"][1]["minScore"] >= 0.95,
            "Lighthouse must enforce performance >=90 and accessibility >=95 across route families",
        ),
        independent_reproduction,
        ReleaseGate(
            "submission_checklist",
            "- [ ]" not in checklist,
            "submission checklist still contains intentionally open items",
        ),
    ]
    deferred_names = {
        gate.name
        for gate, allowed in [
            (independent_reproduction, allow_pending_independent_reproduction),
            (zenodo_doi, allow_pending_zenodo_doi),
        ]
        if allowed and not gate.passed
    }
    failed = [gate for gate in gates if not gate.passed and gate.name not in deferred_names]
    production_failed = [gate for gate in gates if not gate.passed]
    return {
        "schema_version": "0.7.0",
        "release_candidate": "v1.0.0-publication-readiness",
        "production_release_ready": not production_failed,
        "required_gates_passed": not failed,
        "release_status": "ready"
        if not production_failed
        else "staged"
        if not failed
        else "blocked",
        "gates": [asdict(gate) for gate in gates],
        "blocking_reasons": [f"{gate.name}: {gate.detail}" for gate in failed],
        "deferred_reasons": [
            f"{gate.name}: {gate.detail}"
            for gate in production_failed
            if gate.name in deferred_names
        ],
    }


def write_publication_readiness(
    path: str = DEFAULT_OUTPUT,
    *,
    allow_pending_independent_reproduction: bool = False,
    allow_pending_zenodo_doi: bool = False,
) -> dict[str, Any]:
    """Write the publication-readiness audit without waiving blocked gates."""

    report = publication_readiness(
        allow_pending_independent_reproduction=allow_pending_independent_reproduction,
        allow_pending_zenodo_doi=allow_pending_zenodo_doi,
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    """Write readiness status and optionally require a production-ready state."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--require-production", action="store_true")
    parser.add_argument("--allow-pending-independent-reproduction", action="store_true")
    parser.add_argument("--allow-pending-zenodo-doi", action="store_true")
    args = parser.parse_args()
    report = write_publication_readiness(
        args.output,
        allow_pending_independent_reproduction=args.allow_pending_independent_reproduction,
        allow_pending_zenodo_doi=args.allow_pending_zenodo_doi,
    )
    print(
        f"publication release status: {report['release_status']} "
        f"({len(report['blocking_reasons'])} blocking gate(s))"
    )
    return int(args.require_production and not report["required_gates_passed"])


if __name__ == "__main__":
    raise SystemExit(main())
