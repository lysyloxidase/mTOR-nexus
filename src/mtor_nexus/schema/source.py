"""Evidence-source identifiers used by the Phase 2 atlas."""

from enum import StrEnum


class EvidenceSource(StrEnum):
    """Independent resources that can support or reconcile graph claims."""

    UNIPROT = "uniprot"
    PDB = "pdb"
    REACTOME = "reactome"
    KEGG = "kegg"
    STRING = "string"
    BIOGRID = "biogrid"
    PHOSPHOSITEPLUS = "phosphositeplus"
    CHEMBL = "chembl"
    LITERATURE = "literature"
    CURATED = "curated"
