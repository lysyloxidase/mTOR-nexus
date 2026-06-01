"""Validate fail-closed Phase 7 publication-readiness tooling."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from mtor_nexus.release import figures
from mtor_nexus.release.figures import (
    figure_checksums_match,
    figure_exports_reproduce,
    write_figures,
)
from mtor_nexus.release.readiness import (
    BIO_RXIV_DOI,
    ORCID,
    publication_readiness,
    write_publication_readiness,
)
from mtor_nexus.release.readiness import main as readiness_main
from mtor_nexus.release.verify import export_manifest_matches, independent_reproduction_report
from mtor_nexus.release.verify import main as verify_main


def test_deterministic_figure_export_and_checksum_tamper_detection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Write byte-stable figures, provenance, and detect modified SVG bytes."""

    monkeypatch.setattr(figures, "_source_revision", lambda: "abc123")
    root = tmp_path / "figures"
    written = write_figures(str(root))
    assert len(written) == 17
    assert figure_checksums_match(str(root))
    assert figure_exports_reproduce(str(root))
    assert "abc123" in (root / "5" / "provenance.md").read_text(encoding="utf-8")
    assert figures.TFEB_STRUCTURE_DOI in (root / "5" / "provenance.md").read_text(encoding="utf-8")
    chart = (root / "readme" / "atlas-summary.svg").read_text(encoding="utf-8")
    assert "<svg" in chart
    assert "263 nodes | 240 evidence-tagged interactions" in chart
    (root / "1" / "module.svg").write_text("tampered\n", encoding="utf-8")
    assert not figure_checksums_match(str(root))
    assert not figure_exports_reproduce(str(root))
    assert not figure_checksums_match(str(tmp_path / "missing"))


def test_committed_reproduction_bytes_match_and_production_remains_blocked() -> None:
    """Separate deterministic-byte success from unearned production readiness."""

    assert export_manifest_matches()
    assert figure_checksums_match()
    assert figure_exports_reproduce()
    report = independent_reproduction_report()
    assert report["export_manifest_matches"] is True
    assert report["figure_checksums_match"] is True
    assert report["figure_exports_reproduce"] is True
    assert report["production_release_ready"] is False


def test_publication_readiness_lists_measured_blockers(tmp_path: Path) -> None:
    """Keep DOI, model, external attestation, and report-caveat blockers visible."""

    report = publication_readiness()
    gates = {gate["name"]: gate["passed"] for gate in report["gates"]}
    assert report["release_status"] == "blocked"
    assert gates["deterministic_figures"]
    assert gates["nomenclature_guards"]
    assert gates["lighthouse_route_families"]
    assert not gates["validated_selectivity_model"]
    assert not gates["zenodo_doi"]
    assert not gates["biorxiv_preprint"]
    assert not gates["independent_reproduction"]
    output = tmp_path / "readiness.json"
    assert write_publication_readiness(str(output)) == json.loads(
        output.read_text(encoding="utf-8")
    )


def test_release_identifier_patterns_accept_real_shapes() -> None:
    """Recognize publication identifiers without accepting placeholders."""

    assert ORCID.fullmatch("0000-0002-1825-0097")
    assert BIO_RXIV_DOI.search("bioRxiv DOI: 10.1101/2026.06.01.123456")
    assert not BIO_RXIV_DOI.search("bioRxiv DOI: pending")


def test_staged_release_audit_does_not_claim_production_readiness() -> None:
    """Keep narrowly deferred workflow gates visible until their stages complete."""

    report = publication_readiness(
        allow_pending_independent_reproduction=True,
        allow_pending_zenodo_doi=True,
    )
    assert report["production_release_ready"] is False
    deferred = "\n".join(report["deferred_reasons"])
    assert "independent_reproduction" in deferred
    assert "zenodo_doi" in deferred


def test_release_cli_modes_report_blocked_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Let local audits pass while production-required mode fails closed."""

    output = tmp_path / "readiness.json"
    monkeypatch.setattr(sys, "argv", ["readiness", "--output", str(output)])
    assert readiness_main() == 0
    monkeypatch.setattr(
        sys,
        "argv",
        ["readiness", "--output", str(output), "--require-production"],
    )
    assert readiness_main() == 1
    monkeypatch.setattr(sys, "argv", ["verify"])
    assert verify_main() == 0
    monkeypatch.setattr(sys, "argv", ["verify", "--require-production"])
    assert verify_main() == 1


def test_zenodo_publish_command_refuses_before_network_access() -> None:
    """Block irreversible DOI publication without mutating the strict audit."""

    readiness = Path("data/release/publication-readiness.json")
    before = readiness.read_bytes()
    result = subprocess.run(
        [sys.executable, "scripts/zenodo_release.py", "--publish"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Zenodo publication blocked" in result.stderr
    assert readiness.read_bytes() == before


def test_clean_runner_attestation_writer_records_structured_provenance(tmp_path: Path) -> None:
    """Emit the GHCR image, commit, and workflow run used by the release gate."""

    output = tmp_path / "attestation.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/write_independent_reproduction_attestation.py",
            "--image",
            "ghcr.io/example/mtor-nexus:v1.0.0",
            "--commit-sha",
            "a" * 40,
            "--github-run-id",
            "123456",
            "--repository",
            "example/mtor-nexus",
            "--output",
            str(output),
        ],
        check=False,
    )
    assert result.returncode == 0
    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["status"] == "passed"
    assert document["commit_sha"] == "a" * 40
    assert document["run_url"] == "https://github.com/example/mtor-nexus/actions/runs/123456"
