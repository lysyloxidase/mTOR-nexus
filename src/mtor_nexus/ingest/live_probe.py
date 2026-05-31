"""Optional live probes for open pathway-overlay endpoints."""

import argparse
import json
from dataclasses import asdict, dataclass
from urllib.request import Request, urlopen
from xml.etree import ElementTree


@dataclass(frozen=True)
class OverlayProbe:
    """Small endpoint health summary without redistributed raw records."""

    source: str
    identifier: str
    record_count: int
    endpoint: str


def _read(url: str) -> bytes:
    """Read one upstream endpoint with an atlas user agent."""

    request = Request(url, headers={"User-Agent": "mTOR-NEXUS/0.2 live-probe"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def probe_kegg(pathway: str = "hsa04150") -> OverlayProbe:
    """Count relations in the public KEGG KGML overlay."""

    endpoint = f"https://rest.kegg.jp/get/{pathway}/kgml"
    root = ElementTree.fromstring(_read(endpoint))
    return OverlayProbe("kegg", pathway, len(root.findall("relation")), endpoint)


def probe_reactome(pathway: str = "R-HSA-165159") -> OverlayProbe:
    """Count contained events in the Reactome pathway overlay."""

    endpoint = f"https://reactome.org/ContentService/data/pathway/{pathway}/containedEvents"
    events = json.loads(_read(endpoint))
    return OverlayProbe("reactome", pathway, len(events), endpoint)


def probe_string() -> OverlayProbe:
    """Count high-confidence interactions in a small STRING service probe."""

    endpoint = (
        "https://string-db.org/api/tsv-no-header/network"
        "?identifiers=MTOR%0dRPTOR%0dRICTOR&species=9606&required_score=700"
    )
    interactions = [line for line in _read(endpoint).decode("utf-8").splitlines() if line]
    return OverlayProbe("string", "9606:MTOR,RPTOR,RICTOR", len(interactions), endpoint)


def main() -> int:
    """Probe open pathway overlays without writing raw records."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    probes = [probe_kegg(), probe_reactome(), probe_string()]
    if args.json:
        print(json.dumps([asdict(probe) for probe in probes], indent=2, sort_keys=True))
    else:
        for probe in probes:
            print(f"{probe.source}: {probe.identifier}: {probe.record_count} record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
