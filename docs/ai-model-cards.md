# AI Model Cards

Author: [`lysyloxidase`](https://github.com/lysyloxidase).

## Release Policy

The Phase 6 prerelease exposes an applicability-domain gate, transparent
readiness audit, external cofolding handoff, resistance triage, and red-tagged
scaffold exploration. It does **not** ship a validated numerical selectivity
model. Research use only. It is not a clinical decision-support system.

Every computational hypothesis remains tier `speculative`, species flag
`computational`, and `required_experimental_validation=true`.

## Selectivity GNN

**Name and version:** mTOR-vs-PIKK/PI3K selectivity GNN architecture contract,
`0.6.0-prerelease`. **Owner:** mTOR-NEXUS maintainers. **Release date:**
2026-06-01.

**Intended use:** Future research triage of MTOR, PIK3CA, ATM, ATR, and PRKDC
pIC50 values after a trained artifact passes the locked gates below.
**Out-of-scope use:** Clinical decisions, dosing, safety claims, autonomous
compound selection, and any numerical inference from the current prerelease.

**Architecture:** Chemprop-style directed message-passing network, hidden size
300, depth 5, ensemble size 5, dropout 0.2. The registered input contract adds
frozen KLIFS 85-residue aligned-pocket descriptors per target. Uncertainty is
registered as ensemble plus Monte-Carlo dropout, temperature scaling, and split
conformal intervals.

**Current dataset audit:** The committed ChEMBL-derived snapshot has 23
compounds and 275 labels. Compound coverage by task is MTOR 16, PIK3CA 11, ATM
2, ATR 7, and PRKDC 7. KLIFS descriptor ingestion is pending. No validated
artifact digest exists.

**Serving policy:** Invalid SMILES are refused. Molecules below Morgan radius-2
2048-bit nearest-neighbor Tanimoto `0.3` are refused with
`out-of-applicability-domain - prediction unreliable`. In-domain molecules are
also refused until the locked scientific gates pass. No pIC50 value is emitted.

**Known limitations and bias:** The current catalog is small, inhibitor-focused,
and heavily imbalanced across targets. Sparse ATM, ATR, and PRKDC coverage makes
split quality gates impossible to measure honestly.

**Reproducibility:** Run `make data` and `make ai-validate`. Inspect
`data/processed/ai-engine-status.json` and `data/processed/ai-validation.json`.

## Boltz-2 Cofolding Handoff

**Name and version:** External Boltz-2 cofolding handoff, `0.6.0-prerelease`.
**Owner:** mTOR-NEXUS maintainers. **Release date:** 2026-06-01.

**Intended use:** Prepare reviewed-sequence YAML for an external Boltz-2
protein-ligand structure and affinity run. **Out-of-scope use:** Treating a
prepared template as a pose, affinity measurement, or validated binding claim.

The repository bundles neither Boltz weights nor an mTOR construct sequence.
The UI and API emit no affinity or pose-confidence number. A researcher must
review the construct, run Boltz externally, and validate any result
experimentally. The upstream Boltz-2 evaluation files and updated training
information are still documented upstream as pending.

## Resistance Triage

**Name and version:** Binding-mode resistance triage, `0.6.0-prerelease`.
**Owner:** mTOR-NEXUS maintainers. **Release date:** 2026-06-01.

**Intended use:** Surface curated structural liabilities A2034V and F2108L for
FRB-site compounds and M2327I for ATP-site compounds. Rapalog-like FRB
inhibition also surfaces an AKT-inhibitor combination hypothesis based on
feedback reactivation. **Out-of-scope use:** Predicting patient resistance or
recommending treatment.

Outputs are computational triage hypotheses even when they reuse curated
structural residues. They require human review and experimental validation.

## Scaffold Explorer

**Name and version:** Deterministic scaffold explorer, `0.6.0-prerelease`.
**Owner:** mTOR-NEXUS maintainers. **Release date:** 2026-06-01.

**Intended use:** Exercise the prerelease selection and validation workflow with
small, deterministic exploratory scaffolds. **Out-of-scope use:** Claiming
novel molecules, optimized candidates, ADMET predictions, or output from a
trained generative model.

This is heuristic enumeration, not a VAE. RDKit-derived MW, cLogP, HBD, HBA,
and rotatable-bond notes are transparent filters. Every result is tagged
`red_computational_only_unvalidated`, scored only through the refusal-bound
selectivity shell, and marked for experimental validation.

## Locked Scientific Gates

A future validated artifact must record deterministic weights and pass all of
the following without waiver:

| Gate | Required value | Current value |
| --- | --- | --- |
| MTOR test R2 | `>=0.60` | not measured |
| PIK3CA test R2 | `>=0.55` | not measured |
| ATM, ATR, PRKDC test R2 | each `>=0.50` | not measured |
| Selective-vs-nonselective AUROC | `>=0.80` | not measured |
| Conformal empirical coverage | `0.88-0.92` | not measured |
| Torin2 poor-PIKK-selectivity benchmark | required | not measured |
| Deterministic-weight reproducibility | required | not measured |
| Single NVIDIA A100 no-OOM training run | required | not run |

The current selectivity release state is `blocked`. A commit message must not
claim that the Torin2 benchmark passed until a measured artifact proves it.

The accompanying [selectivity training-set datasheet](selectivity-datasheet.md)
records the committed snapshot composition and limitations.
