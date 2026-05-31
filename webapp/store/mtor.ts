"use client";

import { create } from "zustand";
import type { Lens } from "@/lib/visual";

interface MTORStore {
  selectedNode: string | null;
  selectedModule: string;
  lens: Lens;
  flyThroughRun: number;
  selectNode: (nodeId: string | null, moduleId?: string) => void;
  selectModule: (moduleId: string) => void;
  setLens: (lens: Lens) => void;
  startFlyThrough: () => void;
}

export const useMTORStore = create<MTORStore>((set) => ({
  selectedNode: null,
  selectedModule: "2",
  lens: "localization",
  flyThroughRun: 0,
  selectNode: (selectedNode, selectedModule) =>
    set((state) => ({ selectedNode, selectedModule: selectedModule ?? state.selectedModule })),
  selectModule: (selectedModule) => set({ selectedModule }),
  setLens: (lens) => set({ lens }),
  startFlyThrough: () => set((state) => ({ flyThroughRun: state.flyThroughRun + 1 })),
}));
