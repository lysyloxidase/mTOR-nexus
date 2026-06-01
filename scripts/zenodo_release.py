#!/usr/bin/env python3
"""Fail-closed Zenodo production DOI publication for a validated release.

The default action is a local preflight. Publishing is irreversible and must be
requested explicitly with --publish after every production gate passes.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, cast

from mtor_nexus.release.readiness import write_publication_readiness

DEFAULT_API_BASE = "https://zenodo.org/api"
DEFAULT_TAG = "v1.0.0"


def _run(*command: str) -> None:
    """Run one bounded local release-build command."""

    subprocess.run(command, check=True)


def _sha256(path: Path) -> str:
    """Calculate one release-file SHA-256 checksum."""

    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for block in iter(lambda: artifact.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _request_json(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
    data: bytes | None = None,
) -> dict[str, Any]:
    """Send an authenticated Zenodo JSON request."""

    headers = {"Authorization": f"Bearer {token}"}
    body = data
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode()
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310
        return cast(dict[str, Any], json.load(response))


def _copy_release_artifacts(stage: Path) -> None:
    """Copy validated archival artifacts into a bundle staging directory."""

    for source in [
        "data/models/selectivity-gnn-v1.0.pt",
        "docs/release-pdfs/ai-model-cards.pdf",
        "docs/release-pdfs/selectivity-datasheet.pdf",
        "docs/release-pdfs/caveats.pdf",
        "figures",
        "data/processed/ai-engine-status.json",
        "data/processed/ai-validation.json",
        "data/processed/export-manifest.json",
        "data/release/independent-reproduction-passed.json",
        "data/release/publication-readiness.json",
    ]:
        path = Path(source)
        destination = stage / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, destination)
        else:
            shutil.copy2(path, destination)
    shutil.copytree("data/processed/parquet", stage / "mtor-graph-v1.0.parquet")


def build_release_bundle(tag: str, output_dir: str) -> Path:
    """Build wheel, sdist, reproduction image archive, and release ZIP."""

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _run("uv", "build", "--out-dir", str(output / "python"))
    image = f"mtor-nexus-reproduction:{tag}"
    _run("docker", "build", "--file", "Dockerfile.repro", "--tag", image, ".")
    _run("docker", "save", "--output", str(output / f"mtor-nexus-{tag}-docker.tar"), image)
    with tempfile.TemporaryDirectory() as tempdir:
        stage = Path(tempdir) / f"mtor-nexus-{tag}"
        stage.mkdir()
        _copy_release_artifacts(stage)
        shutil.copytree(output / "python", stage / "python")
        shutil.copy2(output / f"mtor-nexus-{tag}-docker.tar", stage / "docker-image.tar")
        source_archive = stage / f"mtor-nexus-{tag}-source.zip"
        _run("git", "archive", "--format=zip", f"--output={source_archive}", "HEAD")
        files = sorted(path for path in stage.rglob("*") if path.is_file())
        (stage / "SHA256SUMS").write_text(
            "".join(f"{_sha256(path)}  {path.relative_to(stage)}\n" for path in files),
            encoding="utf-8",
        )
        archive = output / f"mtor-nexus-{tag}-zenodo.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    bundle.write(path, path.relative_to(stage.parent))
    return archive


def publish_to_zenodo(api_base: str, token: str, archive: Path) -> str:
    """Create, upload, and irreversibly publish one Zenodo deposition."""

    deposition = _request_json("POST", f"{api_base}/deposit/depositions", token, {})
    deposition_id = deposition["id"]
    bucket_url = cast(dict[str, str], deposition["links"])["bucket"]
    metadata = cast(dict[str, Any], json.loads(Path(".zenodo.json").read_text(encoding="utf-8")))
    _request_json(
        "PUT",
        f"{api_base}/deposit/depositions/{deposition_id}",
        token,
        {"metadata": metadata},
    )
    _request_json("PUT", f"{bucket_url}/{archive.name}", token, data=archive.read_bytes())
    published = _request_json(
        "POST",
        f"{api_base}/deposit/depositions/{deposition_id}/actions/publish",
        token,
    )
    doi = published.get("doi")
    if not isinstance(doi, str) or not doi:
        raise RuntimeError("Zenodo publish response did not contain a DOI")
    return doi


def update_doi_metadata(doi: str) -> None:
    """Write minted DOI metadata for a follow-up pull request."""

    citation = Path("CITATION.cff")
    cff = citation.read_text(encoding="utf-8")
    if "\ndoi: " not in cff:
        cff = cff.replace("title: ", f'doi: "{doi}"\ntitle: ', maxreplace=1)
        citation.write_text(cff, encoding="utf-8")
    readme = Path("README.md")
    content = readme.read_text(encoding="utf-8")
    badge = f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)](https://doi.org/{doi})"
    if badge not in content:
        content = content.replace("# mTOR-NEXUS\n", f"# mTOR-NEXUS\n\n{badge}\n", maxreplace=1)
        readme.write_text(content, encoding="utf-8")


def main() -> int:
    """Run local preflight or explicitly publish a validated release."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--output-dir", default="dist/release")
    parser.add_argument("--release-tag", default=DEFAULT_TAG)
    parser.add_argument("--token-env", default="ZENODO_TOKEN")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--require-production", action="store_true")
    args = parser.parse_args()

    report = write_publication_readiness(allow_pending_zenodo_doi=args.publish)
    if not report["required_gates_passed"]:
        print("Zenodo publication blocked:", file=sys.stderr)
        for reason in report["blocking_reasons"]:
            print(f"- {reason}", file=sys.stderr)
        return int(args.publish or args.require_production)
    if not args.publish:
        print(
            "Zenodo production preflight passed; rerun with --publish for irreversible publication."
        )
        return 0
    token = os.environ.get(args.token_env)
    if not token:
        print(f"missing required {args.token_env} environment variable", file=sys.stderr)
        return 1
    archive = build_release_bundle(args.release_tag, args.output_dir)
    doi = publish_to_zenodo(args.api_base.rstrip("/"), token, archive)
    update_doi_metadata(doi)
    write_publication_readiness()
    print(doi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
