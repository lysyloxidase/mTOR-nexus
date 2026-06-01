import type { StylesheetStyle } from "cytoscape";

export const sbgnStyles: StylesheetStyle[] = [
  {
    selector: "node",
    style: {
      "background-color": "#14382b",
      "border-color": "#8be7aa",
      "border-width": 2,
      color: "#e7f4ec",
      "font-size": 10,
      height: 34,
      label: "data(node_id)",
      "text-margin-y": 22,
      width: 50,
    },
  },
  {
    selector: "node[node_type = 'complex']",
    style: { shape: "round-rectangle", "background-color": "#1f5a68", width: 72 },
  },
  {
    selector: "node[node_type = 'kinase']",
    style: { shape: "ellipse", "background-color": "#1f5943" },
  },
  {
    selector: "node[node_type = 'gtpase']",
    style: { shape: "diamond", "background-color": "#504516" },
  },
  {
    selector: "node[node_type = 'transcription_factor']",
    style: { shape: "hexagon", "background-color": "#512f63" },
  },
  {
    selector: "node:selected, node.synced-selection",
    style: {
      "background-color": "#b8ffd0",
      "border-color": "#ffffff",
      "border-width": 5,
      color: "#ffffff",
      "font-size": 13,
      "font-weight": 700,
    },
  },
  {
    selector: "node.disease-affected",
    style: { "border-width": 6, height: 52, width: 68 },
  },
  {
    selector: "node.disease-hyperactivation",
    style: { "background-color": "#6e2424", "border-color": "#ff6b6b" },
  },
  {
    selector: "node.disease-loss",
    style: { "background-color": "#194f6e", "border-color": "#55c7ff" },
  },
  {
    selector: "node.disease-mixed, node.disease-uncertain",
    style: { "background-color": "#625414", "border-color": "#feca57" },
  },
  {
    selector: "edge",
    style: {
      "curve-style": "bezier",
      "line-color": "#61877a",
      opacity: 0.78,
      "target-arrow-color": "#61877a",
      "target-arrow-shape": "triangle",
      width: 1.6,
    },
  },
  {
    selector: "edge[mechanism = 'binds']",
    style: { "line-style": "dashed", "target-arrow-shape": "none" },
  },
  {
    selector: "edge[mechanism = 'inhibits']",
    style: { "line-color": "#ff6b6b", "target-arrow-color": "#ff6b6b", "target-arrow-shape": "tee" },
  },
  {
    selector: "edge[mechanism = 'phosphorylates']",
    style: { "line-color": "#8be7aa", "target-arrow-color": "#8be7aa" },
  },
  {
    selector: "edge[recruitment_mode = 'tos_motif']",
    style: { "line-color": "#00e5ff", "target-arrow-color": "#00e5ff", width: 3 },
  },
  {
    selector: "edge[recruitment_mode = 'msin1']",
    style: { "line-color": "#ff70a6", "target-arrow-color": "#ff70a6", width: 3 },
  },
  {
    selector: "edge[recruitment_mode = 'flcn_ragc_gdp']",
    style: { "line-color": "#feca57", "target-arrow-color": "#feca57", width: 3 },
  },
  {
    selector: "edge.disease-hyperactivation",
    style: { "line-color": "#ff6b6b", "target-arrow-color": "#ff6b6b", opacity: 1, width: 3.2 },
  },
  {
    selector: "edge.disease-loss",
    style: { "line-color": "#55c7ff", "target-arrow-color": "#55c7ff", opacity: 1, width: 3.2 },
  },
];
