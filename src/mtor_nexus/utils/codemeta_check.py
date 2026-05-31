"""Minimal CodeMeta structural validator."""

import argparse
import json
from pathlib import Path

REQUIRED_KEYS = {"@context", "@type", "name", "version", "license", "codeRepository"}


def main() -> int:
    """Validate required CodeMeta fields."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--codemeta", default="codemeta.json")
    args = parser.parse_args()
    document = json.loads(Path(args.codemeta).read_text(encoding="utf-8"))
    missing = REQUIRED_KEYS - document.keys()
    if missing:
        print(f"missing CodeMeta key(s): {sorted(missing)}")
        return 1
    print("codemeta.json contains required fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
