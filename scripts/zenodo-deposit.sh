#!/usr/bin/env bash
set -euo pipefail

echo "Use: uv run python scripts/zenodo_release.py --require-production" >&2
echo "Publishing is explicit: uv run python scripts/zenodo_release.py --publish" >&2
exit 1
