import Link from "next/link";
import { ModuleDiagram } from "@/components/cytoscape/ModuleDiagram";
import { manuscriptModules } from "@/lib/visual";

export function generateStaticParams() {
  return manuscriptModules.map(([id]) => ({ id }));
}

export default async function ModulePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="detail-main">
      <section className="detail-heading">
        <p className="eyebrow">Publication-oriented pathway diagrams</p>
        <h1>SBGN-PD modules</h1>
        <p className="lede">Select a molecular glyph to synchronize the atlas selection. Each panel exports as a scalable 4x SVG.</p>
      </section>
      <div className="module-tabs">
        {manuscriptModules.map(([moduleId, label]) => (
          <Link className={moduleId === id ? "active" : ""} href={`/module/${moduleId}`} key={moduleId}>{moduleId}. {label}</Link>
        ))}
      </div>
      <ModuleDiagram moduleId={id} />
    </main>
  );
}
