"""Resolve catalog protein symbols to canonical human UniProt accessions."""

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from mtor_nexus.graph.catalog import protein_seeds

UNIPROT_SEARCH = (
    "https://rest.uniprot.org/uniprotkb/search"
    "?query=(gene_exact:{symbol})%20AND%20(organism_id:9606)"
    "&format=tsv&fields=accession,gene_names,reviewed&size=10"
)


def _resolve_symbol(symbol: str, attempts: int = 3) -> tuple[str, str]:
    """Return the preferred reviewed accession for one human gene symbol."""

    request = Request(
        UNIPROT_SEARCH.format(symbol=quote(symbol)),
        headers={"User-Agent": "mTOR-NEXUS/0.2 UniProt-refresh"},
    )
    lines: list[str] = []
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=60) as response:
                lines = response.read().decode("utf-8").splitlines()[1:]
            break
        except (TimeoutError, URLError):
            if attempt == attempts - 1:
                raise
            time.sleep(2**attempt)
    candidates: list[tuple[str, str, str]] = []
    for line in lines:
        accession, genes, reviewed = line.split("\t")
        candidates.append((accession, genes, reviewed))
    if not candidates:
        raise ValueError(f"UniProt did not resolve a human accession for {symbol}")
    reviewed = [candidate for candidate in candidates if candidate[2] == "reviewed"]
    exact_primary = [candidate for candidate in reviewed if candidate[1].split()[0] == symbol]
    accession, _, _ = (exact_primary or reviewed or candidates)[0]
    return symbol, accession


def resolve_catalog_accessions(workers: int = 6) -> dict[str, str]:
    """Resolve all catalog proteins concurrently."""

    symbols = [seed.symbol for seed in protein_seeds()]
    accessions: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_resolve_symbol, symbol): symbol for symbol in symbols}
        for future in as_completed(futures):
            symbol, accession = future.result()
            accessions[symbol] = accession
    return dict(sorted(accessions.items()))


def main() -> int:
    """Refresh the committed derived UniProt snapshot."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/curated/uniprot-accessions.json")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    accessions = resolve_catalog_accessions(args.workers)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(accessions, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"resolved {len(accessions)} canonical human UniProt accession(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
