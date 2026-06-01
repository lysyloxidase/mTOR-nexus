"use client";

import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { useEffect, useMemo, useState } from "react";
import type { DiseaseAssociation, DiseaseDocument, GraphDocument, LayoutDocument } from "@/lib/schema";
import { moduleForNode, nodeEvidence } from "@/lib/visual";
import { useMTORStore } from "@/store/mtor";
import { CameraFlyThrough } from "./CameraFlyThrough";
import { ComplexHull } from "./ComplexHull";
import { EdgeLine } from "./EdgeLine";
import { DiseaseGlow } from "./DiseaseGlow";
import { NodeMesh, type PositionedNode } from "./NodeMesh";
import { PerformanceMonitor } from "./PerformanceMonitor";

const perturbationColor = (association?: DiseaseAssociation) =>
  association?.perturbation === "loss"
    ? "#55c7ff"
    : association?.perturbation === "hyperactivation" ? "#ff6b6b" : association ? "#feca57" : undefined;

function Scene({ diseases, graph, layout }: { diseases: DiseaseDocument; graph: GraphDocument; layout: LayoutDocument }) {
  const lens = useMTORStore((state) => state.lens);
  const selectedNode = useMTORStore((state) => state.selectedNode);
  const selectedDisease = useMTORStore((state) => state.selectedDisease);
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
  const diseaseAssociations = useMemo(
    () => diseases.associations.filter((association) => association.disease_id === selectedDisease),
    [diseases.associations, selectedDisease],
  );
  const diseaseByNode = useMemo(
    () => new Map(diseaseAssociations.map((association) => [association.pathway_node_id, association])),
    [diseaseAssociations],
  );
  const diseaseNodes = useMemo(() => {
    const disease = diseases.disease_classes.find((candidate) => candidate.disease_id === selectedDisease);
    const frequency = new Map(disease?.cohort_frequencies.map((item) => [item.gene_symbol, item.frequency_percent]) ?? []);
    return new Map(diseaseAssociations.map((association) => [association.pathway_node_id, 0.22 + (frequency.get(association.pathway_node_id) ?? 0) / 150]));
  }, [diseaseAssociations, diseases.disease_classes, selectedDisease]);
  return (
    <>
      <ambientLight intensity={1.1} />
      <directionalLight intensity={2.4} position={[25, 42, 55]} />
      <ComplexHull color="#38d996" members={nodes.filter((node) => node.complex_membership.includes("MTORC1"))} />
      <ComplexHull color="#55c7ff" members={nodes.filter((node) => node.complex_membership.includes("MTORC2"))} />
      {graph.edges.map((edge, index) => {
        const source = byId.get(edge.source);
        const target = byId.get(edge.target);
        const diseaseColor = perturbationColor(diseaseByNode.get(edge.source) ?? diseaseByNode.get(edge.target));
        return source && target ? <EdgeLine colorOverride={diseaseColor} edge={edge} key={`${edge.source}-${edge.target}-${index}`} source={source} target={target} /> : null;
      })}
      <NodeMesh
        evidence={evidence}
        diseaseNodes={diseaseNodes}
        lens={lens}
        nodes={nodes}
        onSelect={(node) => selectNode(node.node_id, moduleForNode(node))}
        selectedNode={selectedNode}
      />
      <DiseaseGlow associations={diseaseAssociations} nodes={byId} />
      <CameraFlyThrough nodes={nodes} run={flyThroughRun} />
      <OrbitControls enableDamping makeDefault />
      <PerformanceMonitor />
    </>
  );
}

export function MTORGraph3D({ compact = false }: { compact?: boolean }) {
  const [graph, setGraph] = useState<GraphDocument | null>(null);
  const [layout, setLayout] = useState<LayoutDocument | null>(null);
  const [diseases, setDiseases] = useState<DiseaseDocument | null>(null);
  const startFlyThrough = useMTORStore((state) => state.startFlyThrough);
  useEffect(() => {
    Promise.all([
      fetch("/data/mtor-graph.json").then((response) => response.json() as Promise<GraphDocument>),
      fetch("/data/mtor-3d-layout.json").then((response) => response.json() as Promise<LayoutDocument>),
      fetch("/data/diseases.json").then((response) => response.json() as Promise<DiseaseDocument>),
    ]).then(([nextGraph, nextLayout, nextDiseases]) => {
      setGraph(nextGraph);
      setLayout(nextLayout);
      setDiseases(nextDiseases);
    });
  }, []);
  return (
    <section className={`graph-3d ${compact ? "graph-3d-compact" : ""}`}>
      {!compact && <button className="floating-action" onClick={startFlyThrough}>Run insulin cascade</button>}
      {graph && layout && diseases ? (
        <Canvas camera={{ fov: 46, position: [0, 0, 235] }} dpr={[1, 1.5]}>
          <Scene diseases={diseases} graph={graph} layout={layout} />
        </Canvas>
      ) : <p className="graph-loading">Loading pathway atlas...</p>}
    </section>
  );
}
