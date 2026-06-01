# Drug-Discovery Layer

Phase 5 organizes mTOR-pathway inhibitors into three generations plus the dual
PI3K-mTOR and mTORC2-selective research classes:

| Class | Structural mode | Example |
| --- | --- | --- |
| Generation 1 rapalogs | FKBP12-dependent FRB binding | sirolimus |
| Generation 2 TORKi | mTOR kinase ATP pocket | sapanisertib |
| Generation 2 dual PI3K-mTOR | PI3K-family ATP pockets | dactolisib |
| Generation 3 bi-steric | FRB and ATP sites together | RMC-5552 |
| mTORC2-selective research tool | reported RICTOR-mTOR disruption | JR-AB2-011 |

The normalized public artifact is `data/processed/drug-layer.json`. Every drug
node has one canonical ID, a ChEMBL compound ID, registered aliases, and at
least one mechanism edge with evidence tier and species tags. Alias lookup
normalizes punctuation, so `sapanisertib`, `MLN0128`, `INK128`, and `TAK-228`
resolve to one node.

## ChEMBL training snapshot

`make drug-refresh` reads the public ChEMBL API and writes
`data/curated/chembl-bioactivity.json`. RDKit parses, cleans, parent-normalizes,
and canonically serializes every compound SMILES. The committed Phase 5
snapshot retains IC50, Ki, and Kd labels against MTOR, PIK3CA, ATM, ATR, and
PRKDC/DNA-PK for the Phase 6 selectivity model.

The public API was used to reconcile report identifiers. PIK3CA is
`CHEMBL4005`; the supplied `CHEMBL4040` identifier resolves to MAPK1.

## Binding-mode viewer

The browser route `/drug/[id]` embeds Mol* models anchored to RCSB PDB
structures: `4JSV` for FRB context, `4JT6` for the ATP pocket, and `6ZWM` for
mTORC2 context. FRB resistance residues A2034V and F2108L and kinase-domain
residue M2327I are annotated in the structural map. The bi-steric dual-site
display is a mechanistic composite rather than a deposited ternary structure.
