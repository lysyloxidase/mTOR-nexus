"use client";

import { useState } from "react";

export function StructureViewer({ pdbIds }: { pdbIds: string[] }) {
  const [pdbId, setPdbId] = useState(pdbIds[0]);
  if (!pdbId) return <p className="muted">No structural model is linked to this node.</p>;
  return (
    <section className="structure-viewer">
      <div className="structure-toolbar">
        <h2>Mol* structure viewer</h2>
        <label>
          PDB model
          <select value={pdbId} onChange={(event) => setPdbId(event.target.value)}>
            {pdbIds.map((id) => <option key={id}>{id}</option>)}
          </select>
        </label>
      </div>
      <iframe
        allow="fullscreen"
        loading="lazy"
        src={`https://molstar.org/viewer/?pdb=${pdbId.toLowerCase()}`}
        title={`Mol* structure viewer for PDB ${pdbId}`}
      />
    </section>
  );
}
