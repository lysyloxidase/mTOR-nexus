"""Node model for the heterogeneous mTOR knowledge graph."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class NodeType(StrEnum):
    """Supported biological and pharmacological node categories."""

    KINASE = "kinase"
    GTPASE = "gtpase"
    SCAFFOLD = "scaffold"
    SUBSTRATE = "substrate"
    REGULATOR = "regulator"
    PHOSPHATASE = "phosphatase"
    COMPLEX = "complex"
    METABOLITE = "metabolite"
    SMALL_MOLECULE = "small_molecule"
    TRANSCRIPTION_FACTOR = "transcription_factor"
    RECEPTOR = "receptor"
    SENSOR = "sensor"
    LIPID = "lipid"


class SubcellularLocation(StrEnum):
    """Locations used by the pathway atlas."""

    LYSOSOME = "lysosome"
    CYTOPLASM = "cytoplasm"
    PLASMA_MEMBRANE = "plasma_membrane"
    NUCLEUS = "nucleus"
    MITOCHONDRIA = "mitochondria"
    MAM = "mitochondria_associated_membrane"
    STRESS_GRANULE = "stress_granule"
    ER = "endoplasmic_reticulum"


PROTEIN_NODE_TYPES = {
    NodeType.KINASE,
    NodeType.GTPASE,
    NodeType.SCAFFOLD,
    NodeType.SUBSTRATE,
    NodeType.REGULATOR,
    NodeType.PHOSPHATASE,
    NodeType.TRANSCRIPTION_FACTOR,
    NodeType.RECEPTOR,
    NodeType.SENSOR,
}


class MTORNode(BaseModel):
    """A graph node with stable identifiers and primary evidence."""

    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(min_length=1)
    gene_symbol: str | None = None
    protein_name: str = Field(min_length=1)
    uniprot_id: str | None = None
    chebi_id: str | None = None
    chembl_id: str | None = None
    node_type: NodeType
    pathway_role: str = Field(min_length=1)
    localization: list[SubcellularLocation] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    pdb_ids: list[str] = Field(default_factory=list)
    complex_membership: list[str] = Field(default_factory=list)
    disease_associations: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    druggable: bool = False
    primary_citations: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def proteins_have_uniprot_accessions(self) -> "MTORNode":
        """Require stable accessions for all protein-like nodes."""

        if self.node_type in PROTEIN_NODE_TYPES and not self.uniprot_id:
            raise ValueError("protein nodes require a UniProt accession")
        return self
