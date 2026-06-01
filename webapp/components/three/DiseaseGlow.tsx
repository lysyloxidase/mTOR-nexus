"use client";

import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";
import type { DiseaseAssociation } from "@/lib/schema";
import type { PositionedNode } from "./NodeMesh";

const perturbationColor = (perturbation: DiseaseAssociation["perturbation"]) =>
  perturbation === "loss" ? "#55c7ff" : perturbation === "hyperactivation" ? "#ff6b6b" : "#feca57";

function PulsingGlow({ association, node }: { association: DiseaseAssociation; node: PositionedNode }) {
  const mesh = useRef<THREE.Mesh>(null);
  useFrame(({ clock }) => {
    if (!mesh.current) return;
    mesh.current.scale.setScalar(1 + Math.sin(clock.elapsedTime * 3.2) * 0.16);
  });
  return (
    <mesh position={[node.x, node.y, node.z]} ref={mesh}>
      <sphereGeometry args={[4.3, 12, 10]} />
      <meshBasicMaterial
        color={perturbationColor(association.perturbation)}
        depthWrite={false}
        opacity={0.22}
        transparent
      />
    </mesh>
  );
}

export function DiseaseGlow({
  associations,
  nodes,
}: {
  associations: DiseaseAssociation[];
  nodes: Map<string, PositionedNode>;
}) {
  return associations.map((association) => {
    const node = nodes.get(association.pathway_node_id);
    return node ? <PulsingGlow association={association} key={association.pathway_node_id} node={node} /> : null;
  });
}
