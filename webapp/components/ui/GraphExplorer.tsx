"use client";

import dynamic from "next/dynamic";
import { useState } from "react";

const ActiveGraphExplorer = dynamic(
  () => import("./ActiveGraphExplorer").then((module) => module.ActiveGraphExplorer),
  {
    loading: () => <p className="graph-loading">Loading pathway explorer...</p>,
    ssr: false,
  },
);

export function GraphExplorer() {
  const [active, setActive] = useState(false);
  return (
    <main className="explorer-main">
      {active ? (
        <ActiveGraphExplorer />
      ) : (
        <section className="explorer-intro">
          <p className="eyebrow">Global 3D pathway explorer</p>
          <h1>Pathway atlas</h1>
          <p className="lede">
            Load the interactive workspace to explore synchronized 3D and SBGN-PD
            views, evidence lenses, disease overlays, and node-level citations.
          </p>
          <button className="graph-activation-button" onClick={() => setActive(true)}>
            Launch pathway explorer
          </button>
        </section>
      )}
    </main>
  );
}
