import type { MTOREdge, MTORNode } from "@/lib/schema";

const sitePosition = (site: string, index: number, count: number) => {
  const residue = Number(site.replace(/[^0-9]/g, ""));
  if (Number.isFinite(residue) && residue > 0) return Math.min(96, Math.max(4, (residue % 1900) / 19));
  return ((index + 1) / (count + 1)) * 100;
};

export function PhosphoSiteViewer({ node, edges }: { node: MTORNode; edges: MTOREdge[] }) {
  const sites = [
    ...new Map(
      edges
        .filter((edge) => edge.target === node.node_id && edge.phospho_site)
        .map((edge) => [edge.phospho_site, edge]),
    ).values(),
  ];
  if (!sites.length) return <p className="muted">No curated phosphosite edges for this node.</p>;
  return (
    <div className="phospho-viewer" aria-label={`${node.node_id} phosphosite track`}>
      <div className="protein-track" />
      {sites.map((edge, index) => (
        <span
          className="phospho-marker"
          key={`${edge.source}-${edge.phospho_site}`}
          style={{ left: `${sitePosition(edge.phospho_site ?? "", index, sites.length)}%` }}
          title={`${edge.source} -> ${node.node_id} ${edge.phospho_site}`}
        >
          <i>P</i>
          <small>{edge.phospho_site}</small>
        </span>
      ))}
    </div>
  );
}
