# Selectivity Training-Set Datasheet

Author: [`lysyloxidase`](https://github.com/lysyloxidase).

This datasheet follows the documentation goals of Gebru et al. (2021) for the
committed Phase 6 selectivity-training snapshot. It describes the available
data honestly; it is not a statement that the registered model is trainable or
validated.

## Motivation

The snapshot was assembled to evaluate whether an mTOR-vs-PIKK/PI3K
counter-screen model can be trained for research triage. The registered targets
are MTOR, PIK3CA, ATM, ATR, and PRKDC. It must not be used for clinical
decisions, dosing, safety claims, or autonomous candidate nomination.

## Composition

The committed ChEMBL-derived snapshot is
`data/curated/chembl-bioactivity.json`. It contains 23 catalog compounds and
275 selected IC50, Ki, or Kd labels with assay metadata.

| Target | Compounds | Labels | Minimum compounds for registered split gate | Ready |
| --- | ---: | ---: | ---: | --- |
| MTOR | 16 | 157 | 30 | no |
| PIK3CA | 11 | 95 | 30 | no |
| ATM | 2 | 3 | 30 | no |
| ATR | 7 | 9 | 30 | no |
| PRKDC | 7 | 11 | 30 | no |

The compounds are an inhibitor-focused seed catalog, not an unbiased sample of
chemical space. Coverage is sparse and heavily imbalanced.

## Collection Process

`make drug-refresh` queries the public ChEMBL API for the registered catalog,
resolves structures, standardizes SMILES with RDKit, and retains selected
bioactivity records with assay identifiers, descriptions, and confidence
scores. The committed snapshot is derived from the public API and is
redistributable under the source policy documented in `docs/data-sources.md`.

## Preprocessing

RDKit-standardized SMILES are stored beside canonical upstream SMILES. The
current applicability-domain gate uses Morgan radius-2, 2048-bit fingerprints
with a nearest-neighbor Tanimoto threshold of `0.3`.

KLIFS 85-residue aligned pocket descriptors are registered in the future
architecture contract but have not been ingested.

## Uses and Limitations

The snapshot supports data-density auditing, API refusal tests, and future
pipeline development. It does not support an honest train/validation/test claim
for the locked five-target model. ATM, ATR, and PRKDC are particularly sparse.
No validated weights, calibrated conformal intervals, Torin2 benchmark result,
or deterministic A100 training artifact exists.

## Distribution and Maintenance

The snapshot is committed for reproducibility. Refreshes must preserve source
provenance, update the readiness report, and undergo review before release.
Raw licensed COSMIC and PhosphoSitePlus records remain outside this dataset.
