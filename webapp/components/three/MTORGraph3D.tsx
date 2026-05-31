"use client";

import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { useEffect, useMemo, useState } from "react";
import type { GraphDocument, LayoutDocument } from "@/lib/schema";
import { moduleForNode, nodeEvidence } from "@/lib/visual";
import { useMTORStore } from "@/store/mtor";
import { CameraFlyThrough } from "./CameraFlyThrough";
import { ComplexHull } from "./ComplexHull";
import { EdgeLine } from "./EdgeLine";
import { NodeMesh, type PositionedNode } from "./NodeMesh";
import { PerformanceMonitor } from "./PerformanceMonitor";

function Scene({ graph, layout }: { graph: GraphDocument; layout: LayoutDocument }) {
  const lens = useMTORStore((state) => state.lens);
  const selectedNode = useMTORStore((state) => state.selectedNode);
  const selectNode = useMTORStore((state) => state.selectNode);
  const flyThroughRun = useMTORStore((state) => state.flyThroughRun);
  const positions = useMemo(() => new Map(layout.nodes.map((node) => [node.id, node])), [layout]);
  const nodes = useMemo(
    () =>
      graph.nodes.map((node) => ({ ...node, ...positions.get(node.node_id) })) as PositionedNode[],
    [graph.nodes, positions],
  );
  const byId = useMemo(() => new Map(nodes.map((node) => [node.node_id, node])), [nodes]);
  const evidence = useMemo(() => nodeEvidence(graph.nodes, graph.edges), [graph]);
  return (
    <>
      <ambientLight intensity={1.1} />
      <directionalLight intensity={2.4} position={[25, 42, 55]} />
      <ComplexHull color="#38d996" members={nodes.filter((node) => node.complex_membership.includes("MTORC1"))} />
      <ComplexHull color="#55c7ff" members={nodes.filter((node) => node.complex_membership.includes("MTORC2"))} />
      {graph.edges.map((edge, index) => {
        const source = byId.get(edge.source);
        const target = byId.get(edge.target);
        return source && target ? <EdgeLine edge={edge} key={`${edge.source}-${edge.target}-${index}`} source={source} target={target} /> : null;
      })}
      <NodeMesh
        evidence={evidence}
        lens={lens}
        nodes={nodes}
        onSelect={(node) => selectNode(node.node_id, moduleForNode(node))}
        selectedNode={selectedNode}
      />
      <CameraFlyThrough nodes={nodes} run={flyThroughRun} />
      <OrbitControls enableDamping makeDefault />
      <PerformanceMonitor />
    </>
  );
}

export function MTORGraph3D({ compact = false }: { compact?: boolean }) {
  const [graph, setGraph] = useState<GraphDocument | null>(null);
  const [layout, setLayout] = useState<LayoutDocument | null>(null);
  const startFlyThrough = useMTORStore((state) => state.startFlyThrough);
  useEffect(() => {
    Promise.all([
      fetch("/data/mtor-graph.json").then((response) => response.json() as Promise<GraphDocument>),
      fetch("/data/mtor-3d-layout.json").then((response) => response.json() as Promise<LayoutDocument>),
    ]).then(([nextGraph, nextLayout]) => {
      setGraph(nextGraph);
      setLayout(nextLayout);
    });
  }, []);
  return (
    <section className={`graph-3d ${compact ? "graph-3d-compact" : ""}`}>
      {!compact && <button className="floating-action" onClick={startFlyThrough}>Run insulin cascade</button>}
      {graph && layout ? (
        <Canvas camera={{ fov: 46, position: [0, 0, 235] }} dpr={[1, 1.5]}>
          <Scene graph={graph} layout={layout} />
        </Canvas>
      ) : <p className="graph-loading">Loading pathway atlas...</p>}
    </section>
  );
}
