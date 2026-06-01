"use client";

import { useLayoutEffect, useMemo, useRef } from "react";
import type { ThreeEvent } from "@react-three/fiber";
import * as THREE from "three";
import type { MTORNode, SpeciesEvidence, Tier } from "@/lib/schema";
import type { Lens } from "@/lib/visual";
import { nodeColor } from "@/lib/visual";

export interface PositionedNode extends MTORNode {
  x: number;
  y: number;
  z: number;
}

const nodeTypes = [
  "kinase",
  "gtpase",
  "scaffold",
  "substrate",
  "complex",
  "small_molecule",
  "sensor",
  "transcription_factor",
  "other",
] as const;

const shapeForType = (type: string) => {
  if (type === "kinase") return <sphereGeometry args={[1.65, 14, 10]} />;
  if (type === "gtpase") return <octahedronGeometry args={[1.9]} />;
  if (type === "scaffold") return <boxGeometry args={[2.8, 2.8, 2.8]} />;
  if (type === "substrate") return <cylinderGeometry args={[1.35, 1.35, 3.2, 12]} />;
  if (type === "complex") return <icosahedronGeometry args={[2.55]} />;
  if (type === "small_molecule") return <tetrahedronGeometry args={[1.8]} />;
  if (type === "sensor") return <coneGeometry args={[1.7, 3.5, 12]} />;
  if (type === "transcription_factor") return <torusGeometry args={[1.7, 0.5, 8, 16]} />;
  return <sphereGeometry args={[1.25, 10, 8]} />;
};

function InstancedShape({
  entries,
  type,
  lens,
  evidence,
  selectedNode,
  diseaseNodes,
  onSelect,
}: {
  entries: PositionedNode[];
  type: string;
  lens: Lens;
  evidence: Map<string, { tier: Tier; species: SpeciesEvidence[] }>;
  selectedNode: string | null;
  diseaseNodes: Map<string, number>;
  onSelect: (node: PositionedNode) => void;
}) {
  const mesh = useRef<THREE.InstancedMesh>(null);
  useLayoutEffect(() => {
    if (!mesh.current) return;
    const transform = new THREE.Object3D();
    const color = new THREE.Color();
    entries.forEach((node, index) => {
      transform.position.set(node.x, node.y, node.z);
      const diseaseScale = diseaseNodes.get(node.node_id) ?? 0;
      transform.scale.setScalar(node.node_id === selectedNode ? 1.65 : 1 + diseaseScale);
      transform.updateMatrix();
      mesh.current?.setMatrixAt(index, transform.matrix);
      mesh.current?.setColorAt(index, color.set(nodeColor(node, lens, evidence)));
    });
    mesh.current.instanceMatrix.needsUpdate = true;
    if (mesh.current.instanceColor) mesh.current.instanceColor.needsUpdate = true;
  }, [diseaseNodes, entries, evidence, lens, selectedNode]);
  const selectInstance = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation();
    if (event.instanceId !== undefined) onSelect(entries[event.instanceId]);
  };
  return (
    <instancedMesh
      args={[undefined, undefined, entries.length]}
      onClick={selectInstance}
      onPointerOut={() => { document.body.style.cursor = "default"; }}
      onPointerOver={() => { document.body.style.cursor = "pointer"; }}
      ref={mesh}
    >
      {shapeForType(type)}
      <meshStandardMaterial roughness={0.42} metalness={0.18} vertexColors />
    </instancedMesh>
  );
}

export function NodeMesh({
  nodes,
  lens,
  evidence,
  selectedNode,
  diseaseNodes,
  onSelect,
}: {
  nodes: PositionedNode[];
  lens: Lens;
  evidence: Map<string, { tier: Tier; species: SpeciesEvidence[] }>;
  selectedNode: string | null;
  diseaseNodes: Map<string, number>;
  onSelect: (node: PositionedNode) => void;
}) {
  const groups = useMemo(() => {
    const grouped = new Map<string, PositionedNode[]>();
    for (const type of nodeTypes) grouped.set(type, []);
    for (const node of nodes) {
      const key = nodeTypes.includes(node.node_type as (typeof nodeTypes)[number])
        ? node.node_type
        : "other";
      grouped.get(key)?.push(node);
    }
    return grouped;
  }, [nodes]);
  return (
    <>
      {nodeTypes.map((type) => {
        const entries = groups.get(type) ?? [];
        return entries.length ? (
          <InstancedShape
            entries={entries}
            diseaseNodes={diseaseNodes}
            evidence={evidence}
            key={type}
            lens={lens}
            onSelect={onSelect}
            selectedNode={selectedNode}
            type={type}
          />
        ) : null;
      })}
    </>
  );
}
