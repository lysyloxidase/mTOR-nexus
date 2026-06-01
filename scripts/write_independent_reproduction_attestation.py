#!/usr/bin/env python3
"""Record a clean-runner reproduction attestation for the Zenodo release gate."""

import argparse
import json
import re
from pathlib import Path

DEFAULT_OUTPUT = "data/release/independent-reproduction-passed.json"
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def write_attestation(
    *,
    image: str,
    commit_sha: str,
    github_run_id: str,
    repository: str,
    output: str = DEFAULT_OUTPUT,
) -> dict[str, str]:
    """Write one structured GitHub Actions attestation after reproduction passes."""

    if not image.startswith("ghcr.io/"):
        raise ValueError("attested image must use ghcr.io")
    if COMMIT_SHA.fullmatch(commit_sha) is None:
        raise ValueError("commit SHA must contain 40 lowercase hexadecimal characters")
    if not github_run_id.isdigit():
        raise ValueError("GitHub Actions run ID must be numeric")
    if "/" not in repository:
        raise ValueError("GitHub repository must use owner/name form")
    document = {
        "schema_version": "0.7.0",
        "status": "passed",
        "recorded_by": "github-actions-independent-reproduction",
        "image": image,
        "commit_sha": commit_sha,
        "github_run_id": github_run_id,
        "run_url": f"https://github.com/{repository}/actions/runs/{github_run_id}",
    }
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return document


def main() -> int:
    """Write an attestation from explicit GitHub Actions values."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--github-run-id", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    write_attestation(
        image=args.image,
        commit_sha=args.commit_sha,
        github_run_id=args.github_run_id,
        repository=args.repository,
        output=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
