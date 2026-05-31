import type { MTOREdge, MTORNode, SpeciesEvidence, Tier } from "./schema";

export type Lens = "localization" | "tier" | "species";

export const manuscriptModules = [
  ["1", "Core complexes"],
  ["2", "Growth factors"],
  ["3", "Amino acids"],
  ["4", "Energy + stress"],
  ["5", "Outputs"],
  ["6", "mTORC2"],
  ["7", "Feedback"],
] as const;

export const moduleForNode = (node: MTORNode): string => {
  if (node.module === "01-core-complexes") return "1";
  if (["02-growth-factor-pi3k-akt", "03-tsc-rheb"].includes(node.module)) return "2";
  if (node.module === "04-amino-acid-sensing") return "3";
  if (["05-energy-sensing", "06-stress-inputs"].includes(node.module)) return "4";
  if (["07-protein-synthesis", "08-autophagy", "09-lipid-nucleotide-synthesis"].includes(node.module)) return "5";
  if (node.module === "10-mtorc2-outputs") return "6";
  return "7";
};

const tierPriority: Record<Tier, number> = { robust: 3, plausible: 2, speculative: 1 };

export const nodeEvidence = (nodes: MTORNode[], edges: MTOREdge[]) => {
  const evidence = new Map<string, { tier: Tier; species: SpeciesEvidence[] }>();
  for (const node of nodes) evidence.set(node.node_id, { tier: "speculative", species: [] });
  for (const edge of edges) {
    for (const id of [edge.source, edge.target]) {
      const entry = evidence.get(id) ?? { tier: "speculative" as Tier, species: [] };
      if (tierPriority[edge.tier] > tierPriority[entry.tier]) entry.tier = edge.tier;
      entry.species = [...new Set([...entry.species, ...edge.species_evidence])];
      evidence.set(id, entry);
    }
  }
  return evidence;
};

const lensColors = {
  localization: {
    lysosome: "#ff9f43",
    cytoplasm: "#54a0ff",
    plasma_membrane: "#48dbb4",
    nucleus: "#c56cf0",
    mitochondria: "#ff6b6b",
    endoplasmic_reticulum: "#feca57",
    unassigned: "#91a7a0",
  },
  tier: { robust: "#38d996", plausible: "#feca57", speculative: "#ff6b6b" },
  species: {
    human: "#38d996",
    human_and_rodent: "#55c7ff",
    rodent: "#feca57",
    structural: "#c56cf0",
    in_vitro_biochemical: "#ff9f43",
    computational: "#ff6b6b",
    unassigned: "#91a7a0",
  },
} as const;

export const nodeColor = (
  node: MTORNode,
  lens: Lens,
  evidence: Map<string, { tier: Tier; species: SpeciesEvidence[] }>,
) => {
  const nodeEntry = evidence.get(node.node_id);
  if (lens === "localization") {
    const location = node.localization[0] as keyof typeof lensColors.localization | undefined;
    return lensColors.localization[location ?? "unassigned"] ?? lensColors.localization.unassigned;
  }
  if (lens === "tier") return lensColors.tier[nodeEntry?.tier ?? "speculative"];
  const species = nodeEntry?.species[0] as keyof typeof lensColors.species | undefined;
  return lensColors.species[species ?? "unassigned"] ?? lensColors.species.unassigned;
};

export const edgeColor = (edge: MTOREdge) => {
  if (edge.recruitment_mode === "tos_motif") return "#00e5ff";
  if (edge.recruitment_mode === "msin1") return "#ff70a6";
  if (edge.recruitment_mode === "flcn_ragc_gdp") return "#feca57";
  if (edge.mechanism === "inhibits") return "#ff6b6b";
  if (edge.mechanism === "phosphorylates") return "#8be7aa";
  if (edge.mechanism === "binds") return "#91a7a0";
  return "#73a8d8";
};
