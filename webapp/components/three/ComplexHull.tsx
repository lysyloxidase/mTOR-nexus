"use client";

import { useMemo } from "react";
import * as THREE from "three";
import { ConvexGeometry } from "three/examples/jsm/geometries/ConvexGeometry.js";
import type { PositionedNode } from "./NodeMesh";

const expansion = [
  new THREE.Vector3(3, 0, 0),
  new THREE.Vector3(-3, 0, 0),
  new THREE.Vector3(0, 3, 0),
  new THREE.Vector3(0, -3, 0),
  new THREE.Vector3(0, 0, 3),
  new THREE.Vector3(0, 0, -3),
];

export function ComplexHull({
  color,
  members,
}: {
  color: string;
  members: PositionedNode[];
}) {
  const hull = useMemo(() => {
    const points = members.flatMap((node) =>
      expansion.map((offset) => new THREE.Vector3(node.x, node.y, node.z).add(offset)),
    );
    return points.length >= 4 ? new ConvexGeometry(points) : null;
  }, [members]);
  if (!hull) return null;
  return (
    <mesh geometry={hull}>
      <meshBasicMaterial color={color} depthWrite={false} opacity={0.08} transparent />
    </mesh>
  );
}
