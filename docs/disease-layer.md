# Disease layer

Phase 4 maps eight evidence-tagged disease classes onto the normalized pathway:
cancer, mTORopathies and epilepsy, neurodegeneration, aging and longevity,
metabolic disease, rare syndromes, immunology and transplant, and
cardiovascular disease.

Each disease-to-pathway association retains an evidence tier, species
provenance, source references, and a perturbation direction. The browser uses
these edges to add pulsing 3D glows, mutation-frequency size modifiers, and
matching Cytoscape highlights. Species caveats remain visible for aging and
metabolic overlays.

## Mutation sources

Open artifacts contain HGVS-validated records with ClinVar and cBioPortal
references. `make disease-probe` recalculates the current TCGA Firehose Legacy
ER-positive breast PIK3CA mutation-only frequency and verifies ClinVar access
for recurrent MTOR `p.Glu1799Lys`.

COSMIC raw records are not redistributed. Curators with a valid local license
may reconcile a TSV snapshot with `mtor_nexus.disease.cosmic_overlay`; the open
atlas retains only the segregation policy and reconciliation status.
