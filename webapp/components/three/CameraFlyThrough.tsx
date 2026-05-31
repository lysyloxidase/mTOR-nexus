"use client";

import { useFrame, useThree } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";
import type { PositionedNode } from "./NodeMesh";

const cascade = ["INSR", "IRS1", "PIK3CA", "AKT1", "TSC2", "RHEB", "MTORC1", "RPS6KB1"];

export function CameraFlyThrough({ nodes, run }: { nodes: PositionedNode[]; run: number }) {
  const camera = useThree((state) => state.camera);
  const previousRun = useRef(run);
  const progress = useRef(0);
  useFrame((_state, delta) => {
    if (previousRun.current !== run) {
      previousRun.current = run;
      progress.current = 0;
    }
    if (!run || progress.current >= cascade.length - 0.01) return;
    progress.current = Math.min(cascade.length - 0.01, progress.current + delta * 0.65);
    const index = Math.floor(progress.current);
    const next = Math.min(index + 1, cascade.length - 1);
    const from = nodes.find((node) => node.node_id === cascade[index]);
    const to = nodes.find((node) => node.node_id === cascade[next]);
    if (!from || !to) return;
    const focus = new THREE.Vector3(from.x, from.y, from.z).lerp(
      new THREE.Vector3(to.x, to.y, to.z),
      progress.current - index,
    );
    camera.position.lerp(focus.clone().add(new THREE.Vector3(0, 9, 35)), 0.09);
    camera.lookAt(focus);
  });
  return null;
}
