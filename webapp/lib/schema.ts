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
  | "lipid";

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
  gene_symbol?: string;
  uniprot_id?: string;
  aliases?: string[];
}

export interface MTOREdge {
  source: string;
  target: string;
  mechanism: string;
  tier: Tier;
  species_evidence: SpeciesEvidence[];
  citations: string[];
  recruitment_mode?: RecruitmentMode;
  phospho_site?: string;
  phosphositeplus_id?: string;
}
