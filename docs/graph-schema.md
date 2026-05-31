# Graph Schema

The source-of-truth Pydantic models live in `src/mtor_nexus/schema`. A mirrored
TypeScript contract lives in `webapp/lib/schema.ts`. Phase 2 also records a
module and source references on nodes, and independent evidence sources plus
source references on edges.

## Nodes

Protein-like nodes require UniProt accessions. Metabolites and small molecules
may carry ChEBI or ChEMBL identifiers. Nodes can also record aliases, domains,
PDB structures, localizations, complex membership, disease associations, and
primary citations.

## Edges

Edges are directed by default and require a mechanism, tier, non-empty
species-evidence list, and primary citations. Phosphorylation edges additionally
require a phospho-site and a PhosphoSitePlus identifier. The normalized graph
ships as JSON, JSON-LD, GraphML, Parquet, and module-focused Cytoscape JSON.

## Recruitment modes

| Mode | Meaning |
| --- | --- |
| `tos_motif` | RAPTOR-mediated recruitment of substrates such as S6K1 and 4E-BP1 |
| `msin1` | mTORC2 substrate engagement |
| `flcn_ragc_gdp` | Non-canonical TFEB-oriented recruitment mode |
| `none` | Edge is not a substrate-recruitment interaction |
