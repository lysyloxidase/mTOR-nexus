# Visualization

Phase 3 provides two synchronized pathway lenses:

- A React Three Fiber global explorer renders the normalized graph using a
  committed deterministic force layout. Node shape encodes biological type,
  while the active lens recolors nodes by localization, evidence tier, or
  species provenance.
- Seven Cytoscape.js SBGN-PD module diagrams reorganize the curation modules
  into manuscript-oriented figures. Canonical node IDs are preserved between
  the 3D and 2D views, so shared Zustand selection highlights both surfaces.

The browser assets in `webapp/public/data/` are generated from the Phase 2
normalized graph by `python -m mtor_nexus.graph.build`. Each module exports a
vector SVG with 4x publication dimensions. Node detail routes add UniProt IDs,
domains, phosphosite tracks, DOI metadata hover cards, and Mol* PDB embeds.

## Visual grammar

Node shapes identify kinases, GTPases, scaffolds, substrates, complexes,
small molecules, sensors, and transcription factors. Edge lines distinguish
activation, inhibition, phosphorylation, binding, and the three substrate
recruitment modes. Translucent convex hulls group mTORC1 and mTORC2 subunits.
