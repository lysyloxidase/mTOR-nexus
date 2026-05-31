"use client";

import cytoscape, { type Core } from "cytoscape";
import { useEffect, useRef, useState } from "react";
import type { ModuleDocument } from "@/lib/schema";
import { useMTORStore } from "@/store/mtor";
import { ExportSVG } from "./ExportSVG";
import { sbgnStyles } from "./SBGNStyle";

export function ModuleDiagram({ moduleId, compact = false }: { moduleId: string; compact?: boolean }) {
  const container = useRef<HTMLDivElement>(null);
  const [cy, setCy] = useState<Core | null>(null);
  const [document, setDocument] = useState<ModuleDocument | null>(null);
  const selectedNode = useMTORStore((state) => state.selectedNode);
  const selectNode = useMTORStore((state) => state.selectNode);
  useEffect(() => {
    fetch(`/data/modules/${moduleId}.json`)
      .then((response) => response.json() as Promise<ModuleDocument>)
      .then(setDocument);
  }, [moduleId]);
  useEffect(() => {
    if (!container.current || !document) return;
    const instance = cytoscape({
      container: container.current,
      elements: [...document.elements.nodes, ...document.elements.edges],
      layout: { name: "preset", fit: true, padding: 42 },
      style: sbgnStyles,
      wheelSensitivity: 0.22,
    });
    instance.on("tap", "node", (event) => selectNode(event.target.id(), moduleId));
    setCy(instance);
    return () => instance.destroy();
  }, [document, moduleId, selectNode]);
  useEffect(() => {
    if (!cy) return;
    cy.nodes().removeClass("synced-selection");
    if (selectedNode) cy.getElementById(selectedNode).addClass("synced-selection");
  }, [cy, selectedNode]);
  return (
    <section className={`module-diagram ${compact ? "module-diagram-compact" : ""}`}>
      <div className="diagram-toolbar">
        <div>
          <p className="panel-kicker">SBGN-PD manuscript module {moduleId}</p>
          <h2>{document?.module.title ?? "Loading module..."}</h2>
        </div>
        <ExportSVG cy={cy} slug={document?.module.slug ?? `module-${moduleId}`} />
      </div>
      <div className="cytoscape-stage" ref={container} />
    </section>
  );
}
