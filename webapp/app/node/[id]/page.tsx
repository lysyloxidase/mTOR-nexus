import { notFound } from "next/navigation";
import { NodeCard } from "@/components/ui/NodeCard";
import { StructureViewer } from "@/components/pdb/StructureViewer";
import type { GraphDocument } from "@/lib/schema";
import graphData from "@/public/data/mtor-graph.json";

const graph = graphData as unknown as GraphDocument;

export function generateStaticParams() {
  return graph.nodes.map((node) => ({ id: node.node_id }));
}

export default async function NodePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const node = graph.nodes.find((candidate) => candidate.node_id === decodeURIComponent(id));
  if (!node) notFound();
  return (
    <main className="detail-main">
      <section className="detail-heading">
        <p className="eyebrow">Molecular detail</p>
        <h1>{node.node_id}</h1>
      </section>
      <div className="node-detail-grid">
        <NodeCard edges={graph.edges} node={node} />
        <StructureViewer pdbIds={node.pdb_ids} />
      </div>
    </main>
  );
}
