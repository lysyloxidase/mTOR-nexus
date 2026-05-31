"use client";

import type { Lens } from "@/lib/visual";
import { useMTORStore } from "@/store/mtor";

const lenses: { id: Lens; label: string }[] = [
  { id: "localization", label: "Localization" },
  { id: "tier", label: "Evidence tier" },
  { id: "species", label: "Species" },
];

export function PathwayLensSwitcher() {
  const lens = useMTORStore((state) => state.lens);
  const setLens = useMTORStore((state) => state.setLens);
  return (
    <div className="lens-switcher" aria-label="Pathway color lens">
      {lenses.map(({ id, label }) => (
        <button className={lens === id ? "active" : ""} key={id} onClick={() => setLens(id)}>
          {label}
        </button>
      ))}
    </div>
  );
}
