"use client";

import { useEffect, useMemo, useState } from "react";
import { ModuleDiagram } from "@/components/cytoscape/ModuleDiagram";
import { MTORGraph3D } from "@/components/three/MTORGraph3D";
import { DiseaseOverlay } from "@/components/disease/DiseaseOverlay";
import type { GraphDocument } from "@/lib/schema";
import { manuscriptModules } from "@/lib/visual";
import { useMTORStore } from "@/store/mtor";
import { LegendPanel } from "./LegendPanel";
import { NodeCard } from "./NodeCard";
import { PathwayLensSwitcher } from "./PathwayLensSwitcher";

export function GraphExplorer() {
  const [graph, setGraph] = useState<GraphDocument | null>(null);
  const selectedNode = useMTORStore((state) => state.selectedNode);
  const selectedModule = useMTORStore((state) => state.selectedModule);
  const selectModule = useMTORStore((state) => state.selectModule);
  useEffect(() => {
    fetch("/data/mtor-graph.json")
      .then((response) => response.json() as Promise<GraphDocument>)
      .then(setGraph);
  }, []);
  const node = useMemo(
    () => graph?.nodes.find((candidate) => candidate.node_id === selectedNode),
    [graph, selectedNode],
  );
  return (
    <main className="explorer-main">
      <section className="explorer-heading">
        <div>
          <p className="eyebrow">Global 3D pathway explorer</p>
          <h1>Pathway atlas</h1>
        </div>
        <PathwayLensSwitcher />
      </section>
      <section className="explorer-grid">
        <MTORGraph3D />
        <aside className="explorer-sidebar">
          <DiseaseOverlay />
          <LegendPanel />
          {node && graph ? <NodeCard compact edges={graph.edges} node={node} /> : (
            <article className="node-card">
              <p className="panel-kicker">Selection</p>
              <h2>Choose a node</h2>
              <p>Click a 3D shape or a glyph in the module diagram to inspect its evidence.</p>
            </article>
          )}
        </aside>
      </section>
      <section className="module-section">
        <div className="module-tabs" aria-label="Manuscript module">
          {manuscriptModules.map(([id, label]) => (
            <button className={selectedModule === id ? "active" : ""} key={id} onClick={() => selectModule(id)}>
              {id}. {label}
            </button>
          ))}
        </div>
        <ModuleDiagram compact moduleId={selectedModule} />
      </section>
    </main>
  );
}
