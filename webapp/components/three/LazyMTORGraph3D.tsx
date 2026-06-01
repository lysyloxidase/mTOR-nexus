"use client";

import dynamic from "next/dynamic";
import { useState } from "react";

const MTORGraph3D = dynamic(
  () => import("./MTORGraph3D").then((module) => module.MTORGraph3D),
  {
    loading: () => <p className="graph-loading">Loading interactive atlas...</p>,
    ssr: false,
  },
);

export function LazyMTORGraph3D({ compact = false }: { compact?: boolean }) {
  const [active, setActive] = useState(false);
  if (active) {
    return <MTORGraph3D compact={compact} />;
  }
  return (
    <section className={`graph-3d graph-activation ${compact ? "graph-3d-compact" : ""}`}>
      <div>
        <p className="eyebrow">Interactive WebGL view</p>
        <h2>Load the 3D atlas when you need it</h2>
        <p>
          The evidence-bearing pathway explorer is loaded on demand to keep the
          initial page fast and accessible.
        </p>
        <button className="graph-activation-button" onClick={() => setActive(true)}>
          Load interactive atlas
        </button>
      </div>
    </section>
  );
}
