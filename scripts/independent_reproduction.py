#!/usr/bin/env python3
"""Container-friendly entry point for deterministic reproduction checks."""

from mtor_nexus.release.verify import main

if __name__ == "__main__":
    raise SystemExit(main())
