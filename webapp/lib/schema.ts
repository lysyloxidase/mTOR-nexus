export type NodeType =
  | "kinase"
  | "gtpase"
  | "scaffold"
  | "substrate"
  | "regulator"
  | "phosphatase"
  | "complex"
  | "metabolite"
  | "small_molecule"
  | "transcription_factor"
  | "receptor"
  | "sensor"
  | "lipid"
  | "condition";

export type Tier = "robust" | "plausible" | "speculative";

export type SpeciesEvidence =
  | "human"
  | "rodent"
  | "human_and_rodent"
  | "in_vitro_biochemical"
  | "structural"
  | "computational";

export type RecruitmentMode = "tos_motif" | "msin1" | "flcn_ragc_gdp" | "none";

export interface MTORNode {
  node_id: string;
  protein_name: string;
  node_type: NodeType;
  pathway_role: string;
  primary_citations: string[];
  module: string;
  source_refs: string[];
  gene_symbol?: string | null;
  uniprot_id?: string | null;
  aliases?: string[];
  localization: string[];
  domains: string[];
  pdb_ids: string[];
  complex_membership: string[];
  disease_associations: string[];
  druggable: boolean;
  chebi_id?: string | null;
  chembl_id?: string | null;
}

export interface MTOREdge {
  source: string;
  target: string;
  mechanism: string;
  tier: Tier;
  species_evidence: SpeciesEvidence[];
  citations: string[];
  evidence_sources: string[];
  source_refs: string[];
  recruitment_mode?: RecruitmentMode;
  phospho_site?: string | null;
  phosphositeplus_id?: string | null;
}

export interface GraphDocument {
  schema_version: string;
  nodes: MTORNode[];
  edges: MTOREdge[];
}

export interface LayoutNode {
  id: string;
  x: number;
  y: number;
  z: number;
}

export interface LayoutDocument {
  schema_version: string;
  layout: string;
  nodes: LayoutNode[];
}

export interface CytoscapeNode {
  data: MTORNode & { id: string };
  position: { x: number; y: number };
}

export interface CytoscapeEdge {
  data: MTOREdge & { id: string };
}

export interface ModuleDocument {
  schema_version: string;
  module: {
    id: string;
    slug: string;
    title: string;
    figure: string;
    source_modules: string[];
  };
  elements: {
    nodes: CytoscapeNode[];
    edges: CytoscapeEdge[];
  };
}
