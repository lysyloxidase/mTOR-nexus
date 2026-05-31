import Link from "next/link";
import type { MTOREdge, MTORNode, Tier } from "@/lib/schema";
import { CitationHoverCard } from "./CitationHoverCard";
import { PhosphoSiteViewer } from "./PhosphoSiteViewer";
import { TierSpeciesBadge } from "./TierSpeciesBadge";

const tierRank: Record<Tier, number> = { robust: 3, plausible: 2, speculative: 1 };

export function NodeCard({
  node,
  edges,
  compact = false,
}: {
  node: MTORNode;
  edges: MTOREdge[];
  compact?: boolean;
}) {
  const relevant = edges.filter((edge) => edge.source === node.node_id || edge.target === node.node_id);
  const strongest = relevant.reduce<Tier>(
    (tier, edge) => tierRank[edge.tier] > tierRank[tier] ? edge.tier : tier,
    "speculative",
  );
  const species = [...new Set(relevant.flatMap((edge) => edge.species_evidence))];
  return (
    <article className="node-card">
      <p className="panel-kicker">{node.node_type.replaceAll("_", " ")}</p>
      <h2>{node.node_id}</h2>
      <p>{node.pathway_role}</p>
      <TierSpeciesBadge tier={strongest} species={species} />
      {node.uniprot_id && <p><strong>UniProt</strong> <a href={`https://www.uniprot.org/uniprotkb/${node.uniprot_id}`} target="_blank" rel="noreferrer">{node.uniprot_id}</a></p>}
      {!!node.domains.length && <p><strong>Domains</strong> {node.domains.join(", ")}</p>}
      {!!node.pdb_ids.length && <p><strong>PDB</strong> {node.pdb_ids.join(", ")}</p>}
      {!compact && <PhosphoSiteViewer node={node} edges={edges} />}
      <div className="citation-list">
        {node.primary_citations.map((doi) => <CitationHoverCard doi={doi} key={doi} tier={strongest} species={species} />)}
      </div>
      {compact && <Link className="text-link" href={`/node/${encodeURIComponent(node.node_id)}`}>Open node detail</Link>}
    </article>
  );
}
