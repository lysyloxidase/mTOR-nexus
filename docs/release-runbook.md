# Production Release Runbook

## Current State

The repository is a `v1.0.0` publication-readiness candidate, not a production
release. Run:

```bash
uv run python scripts/zenodo_release.py
```

This writes `data/release/publication-readiness.json` and reports blockers
without contacting Zenodo.

## Irreversible Publication

Only after every readiness gate passes:

```bash
git tag -s v1.0.0
git push origin v1.0.0
```

The tag workflow requires a signed tag and runs a staged preflight that permits
only the not-yet-possible GHCR attestation and Zenodo DOI gates to remain
pending. It publishes the GHCR reproduction image, runs `make all` and byte
verification on a separate runner, records a structured attestation artifact,
then calls:

```bash
uv run python scripts/zenodo_release.py --publish --require-production
```

Zenodo publication is irreversible. The publisher permits only its own DOI gate
to remain pending during that API call. It updates `README.md` and
`CITATION.cff` only after Zenodo returns the production DOI, writes a strict
post-publication readiness report, and opens the follow-up metadata pull
request.
