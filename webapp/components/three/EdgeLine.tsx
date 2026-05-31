"use client";

import { Html, Line } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";
import type { MTOREdge } from "@/lib/schema";
import { edgeColor } from "@/lib/visual";
import type { PositionedNode } from "./NodeMesh";

export function EdgeLine({
  edge,
  source,
  target,
}: {
  edge: MTOREdge;
  source: PositionedNode;
  target: PositionedNode;
}) {
  const geometry = useMemo(() => {
    const start = new THREE.Vector3(source.x, source.y, source.z);
    const end = new THREE.Vector3(target.x, target.y, target.z);
    const midpoint = start.clone().lerp(end, 0.5);
    const quaternion = new THREE.Quaternion().setFromUnitVectors(
      new THREE.Vector3(0, 1, 0),
      end.clone().sub(start).normalize(),
    );
    return { start, end, midpoint, quaternion };
  }, [source, target]);
  const color = edgeColor(edge);
  const dashed = edge.mechanism === "binds";
  return (
    <>
      <Line
        color={color}
        dashScale={2}
        dashed={dashed}
        lineWidth={edge.recruitment_mode && edge.recruitment_mode !== "none" ? 1.4 : 0.72}
        opacity={0.7}
        points={[geometry.start, geometry.end]}
        transparent
      />
      {edge.mechanism === "inhibits" ? (
        <mesh position={geometry.end} quaternion={geometry.quaternion}>
          <boxGeometry args={[3.8, 0.42, 0.42]} />
          <meshBasicMaterial color={color} />
        </mesh>
      ) : edge.mechanism !== "binds" ? (
        <mesh position={geometry.end} quaternion={geometry.quaternion}>
          <coneGeometry args={[0.9, 2.5, 8]} />
          <meshBasicMaterial color={color} />
        </mesh>
      ) : null}
      {edge.mechanism === "phosphorylates" && (
        <Html center position={geometry.midpoint} sprite transform>
          <span className="phospho-sprite">P</span>
        </Html>
      )}
    </>
  );
}
