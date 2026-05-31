"use client";

import type { Core } from "cytoscape";

const escapeXml = (value: string) =>
  value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

const svgForDiagram = (cy: Core) => {
  const box = cy.elements().boundingBox({ includeLabels: true });
  const padding = 64;
  const width = Math.ceil(box.w + padding * 2);
  const height = Math.ceil(box.h + padding * 2);
  const offsetX = padding - box.x1;
  const offsetY = padding - box.y1;
  const edges = cy.edges().map((edge) => {
    const source = edge.source().position();
    const target = edge.target().position();
    const mechanism = edge.data("mechanism") as string;
    const dash = mechanism === "binds" ? ' stroke-dasharray="8 7"' : "";
    const marker = mechanism === "binds" ? "" : mechanism === "inhibits" ? ' marker-end="url(#tee)"' : ' marker-end="url(#arrow)"';
    return `<path d="M ${source.x + offsetX} ${source.y + offsetY} L ${target.x + offsetX} ${target.y + offsetY}" fill="none" stroke="#547e70" stroke-width="2"${dash}${marker}/>`;
  }).join("");
  const nodes = cy.nodes().map((node) => {
    const { x, y } = node.position();
    const label = escapeXml(node.id());
    const selected = node.hasClass("synced-selection");
    return `<g transform="translate(${x + offsetX} ${y + offsetY})"><rect x="-28" y="-17" width="56" height="34" rx="9" fill="${selected ? "#b8ffd0" : "#14382b"}" stroke="${selected ? "#ffffff" : "#8be7aa"}" stroke-width="${selected ? 4 : 2}"/><text y="35" fill="#dff9e8" font-family="Arial, sans-serif" font-size="11" text-anchor="middle">${label}</text></g>`;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width * 4}" height="${height * 4}" viewBox="0 0 ${width} ${height}" role="img"><defs><marker id="arrow" markerHeight="7" markerWidth="7" orient="auto" refX="6" refY="3.5"><path d="M0,0 L7,3.5 L0,7 z" fill="#547e70"/></marker><marker id="tee" markerHeight="9" markerWidth="7" orient="auto" refX="6" refY="4.5"><path d="M6,0 L6,9" fill="none" stroke="#ff6b6b" stroke-width="2"/></marker></defs><rect width="100%" height="100%" fill="#08130f"/>${edges}${nodes}</svg>`;
};

export function ExportSVG({ cy, slug }: { cy: Core | null; slug: string }) {
  const download = () => {
    if (!cy) return;
    const url = URL.createObjectURL(new Blob([svgForDiagram(cy)], { type: "image/svg+xml" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${slug}-4x.svg`;
    anchor.click();
    URL.revokeObjectURL(url);
  };
  return <button disabled={!cy} onClick={download}>Export SVG (4x)</button>;
}
