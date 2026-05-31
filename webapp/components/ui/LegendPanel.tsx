"use client";

import { useMTORStore } from "@/store/mtor";

const shapes = [
  ["Sphere", "kinase"],
  ["Octahedron", "GTPase"],
  ["Box", "scaffold"],
  ["Cylinder", "substrate"],
  ["Icosahedron", "complex"],
  ["Tetrahedron", "small molecule"],
  ["Cone", "sensor"],
  ["Torus", "transcription factor"],
];

const edgeStyles = [
  ["solid arrow", "activates"],
  ["P + arrow", "phosphorylates"],
  ["tee head", "inhibits"],
  ["dashed", "binds"],
];

export function LegendPanel() {
  const lens = useMTORStore((state) => state.lens);
  return (
    <aside className="legend-panel">
      <p className="panel-kicker">Visual grammar</p>
      <h2>{lens.replace("_", " ")} lens</h2>
      <div className="legend-columns">
        <div>
          <strong>Node shapes</strong>
          {shapes.map(([shape, type]) => <span key={type}>{shape}: {type}</span>)}
        </div>
        <div>
          <strong>Edges</strong>
          {edgeStyles.map(([style, mechanism]) => <span key={mechanism}>{style}: {mechanism}</span>)}
          <span className="recruitment-key">cyan / pink / gold: recruitment mode</span>
        </div>
      </div>
    </aside>
  );
}
