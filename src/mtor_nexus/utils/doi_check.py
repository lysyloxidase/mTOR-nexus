"""Validate bibliography DOIs against Crossref."""

import argparse
import re
from pathlib import Path
from urllib.parse import quote

from mtor_nexus.utils.http_check import resolves

DOI_PATTERN = re.compile(r"doi\s*=\s*[{\"]([^}\"]+)", re.IGNORECASE)
CROSSREF_WORKS_URL = "https://api.crossref.org/works/{doi}"


def extract_dois(bibfile: str) -> list[str]:
    """Extract normalized DOI values from a BibTeX file."""

    content = Path(bibfile).read_text(encoding="utf-8")
    return sorted({doi.strip().lower() for doi in DOI_PATTERN.findall(content)})


def broken_dois(dois: list[str]) -> list[str]:
    """Return DOI values that Crossref cannot resolve."""

    return [doi for doi in dois if not resolves(CROSSREF_WORKS_URL.format(doi=quote(doi, safe="")))]


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--bibfile", default="refs.bib")
    parser.add_argument("--fail-on-broken", action="store_true")
    return parser


def main() -> int:
    """Run DOI validation from the command line."""

    args = build_parser().parse_args()
    dois = extract_dois(args.bibfile)
    failures = broken_dois(dois)
    print(f"checked {len(dois)} DOI(s); broken: {len(failures)}")
    for doi in failures:
        print(f"BROKEN DOI: {doi}")
    return int(bool(args.fail_on_broken and failures))


if __name__ == "__main__":
    raise SystemExit(main())
