"""Live sanity probes for open Phase 4 disease-layer sources."""

import json
from dataclasses import asdict, dataclass
from typing import cast
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CBIOPORTAL = "https://www.cbioportal.org/api"
CLINVAR_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


@dataclass(frozen=True)
class CbioPortalFrequencyProbe:
    """Mutation-only PIK3CA frequency for TCGA ER-positive breast cancer."""

    source: str
    cohort: str
    er_positive_patients: int
    altered_patients: int
    frequency_percent: float


@dataclass(frozen=True)
class ClinvarProbe:
    """ClinVar search count for one required germline mapping."""

    source: str
    query: str
    record_count: int
    first_variation_id: str


def _read_json(url: str) -> object:
    """Read a public JSON API response."""

    request = Request(url, headers={"User-Agent": "mTOR-NEXUS/0.4 live-probe"})
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read())


def probe_cbioportal_pik3ca_er_positive() -> CbioPortalFrequencyProbe:
    """Calculate current TCGA Firehose Legacy ER-positive PIK3CA frequency."""

    mutations = _read_json(
        f"{CBIOPORTAL}/molecular-profiles/brca_tcga_mutations/mutations"
        "?sampleListId=brca_tcga_sequenced&entrezGeneId=5290"
        "&projection=DETAILED&pageSize=100000"
    )
    clinical = _read_json(
        f"{CBIOPORTAL}/studies/brca_tcga/clinical-data?clinicalDataType=PATIENT&projection=DETAILED"
    )
    if not isinstance(mutations, list) or not isinstance(clinical, list):
        raise TypeError("unexpected cBioPortal response shape")
    mutation_records = cast(list[dict[str, object]], mutations)
    clinical_records = cast(list[dict[str, object]], clinical)
    er_positive = {
        str(record["patientId"])
        for record in clinical_records
        if record.get("clinicalAttributeId") == "ER_STATUS_BY_IHC"
        and record.get("value") == "Positive"
    }
    altered = {
        str(record["patientId"])
        for record in mutation_records
        if str(record.get("patientId")) in er_positive
    }
    frequency = len(altered) * 100 / len(er_positive)
    return CbioPortalFrequencyProbe(
        source="cbioportal",
        cohort="brca_tcga:ER_STATUS_BY_IHC=Positive",
        er_positive_patients=len(er_positive),
        altered_patients=len(altered),
        frequency_percent=frequency,
    )


def probe_clinvar(query: str = "MTOR[gene] AND Glu1799Lys") -> ClinvarProbe:
    """Search ClinVar E-utilities for one required germline mapping."""

    parameters = urlencode({"db": "clinvar", "term": query, "retmode": "json"})
    url = f"{CLINVAR_EUTILS}/esearch.fcgi?{parameters}"
    payload = _read_json(url)
    if not isinstance(payload, dict):
        raise TypeError("unexpected ClinVar response shape")
    result = cast(dict[str, object], payload["esearchresult"])
    id_list = cast(list[object], result["idlist"])
    return ClinvarProbe(
        source="clinvar",
        query=query,
        record_count=int(str(result["count"])),
        first_variation_id=str(id_list[0]),
    )


def main() -> int:
    """Print open-source Phase 4 live sanity results."""

    cbioportal = probe_cbioportal_pik3ca_er_positive()
    clinvar = probe_clinvar()
    print(json.dumps({"cbioportal": asdict(cbioportal), "clinvar": asdict(clinvar)}, indent=2))
    if not 25 <= cbioportal.frequency_percent <= 45:
        raise ValueError("PIK3CA ER-positive breast mutation frequency left expected sanity band")
    if clinvar.record_count < 1:
        raise ValueError("ClinVar MTOR p.Glu1799Lys mapping is unavailable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
