# Reviewer Rebuttal Kit

These are draft responses for editorial preparation. They distinguish measured
release facts from work that remains blocked.

## Comment 1: Why model three recruitment modes separately?

The atlas distinguishes `tos_motif`, `msin1`, and `flcn_ragc_gdp` recruitment.
TFEB lacks the TOR signaling motif used by canonical mTORC1 substrates. The
primary cryo-EM entry [PDB 7UXH](https://www.rcsb.org/structure/7UXH) and its
linked Nature paper ([DOI `10.1038/s41586-022-05652-7`](https://doi.org/10.1038/s41586-022-05652-7))
describe RagC-GDP-dependent TFEB presentation to mTORC1. Collapsing these modes
would misrepresent the biology. See `docs/graph-schema.md`.

## Comment 2: Most aging and metabolic claims are rodent-derived. Is that disclosed?

Yes. Every graph edge carries a mandatory species or experimental-context flag.
ITP lifespan extension is tagged `rodent`; PEARL healthspan is represented as
human but early and limited. The disease overlay displays a species-caveat
banner. See `docs/tier-species-rubric.md`.

## Comment 3: AI selectivity within the PIKK family is notoriously hard.

Agreed. The current release candidate does **not** claim a validated numerical
model. The committed training audit reports sparse target coverage, missing
KLIFS descriptors, no validated weights, an unmeasured Torin2 benchmark, and no
A100 run. The API refuses numerical pIC50 output. A future production artifact
must recover mTOR-vs-PI3K selectivity, flag poor ATM/ATR selectivity for Torin2,
pass the locked metrics, and retain explicit out-of-domain refusal.

## Comment 4: Cofolding tools can mis-dock.

Agreed. mTOR-NEXUS only prepares an external Boltz-2 YAML handoff. It bundles no
Boltz weights, emits no pose-confidence or affinity number, and marks every
future cofolding result as requiring experimental validation. A PI3K
mis-docking example should only be added after a primary-source citation is
curated.

## Comment 5: RMC-6236 is an mTOR drug, is it not?

No. `RMC-6236`, `RMC-6291`, and `RMC-9805` are kept out of the bi-steric mTOR
catalog. The mTOR-directed entries are `RMC-5552`, `RMC-6272`, and `RMC-4627`.
This is enforced by `tests/unit/test_nomenclature.py`.

## Comment 6: How are S2448 and S1462 nomenclature mistakes handled?

Hard guards reject both mistakes. mTOR S2448 is represented as RPS6KB1 feedback,
not AKT1 phosphorylation, and no defined function is asserted. TSC2 uses the
canonical AKT site T1462; the invalid `S1462` spelling fails CI. See
`docs/nomenclature-guards.md`.

## Comment 7: Is the software independently reproducible?

The repository now includes a clean-runner Docker workflow and deterministic
checksum verifier for normalized graph exports and publication SVGs. Local
checks pass. Production independent reproduction remains unclaimed until a
published `ghcr.io/lysyloxidase/mtor-nexus:v1.0.0` image completes the separate
runner gate, including the still-blocked Torin2 requirement.

## Comment 8: Has the DOI or preprint already been published?

No. The Zenodo publisher defaults to preflight and refuses network publication
while any production gate is open. bioRxiv submission also remains pending
author action and bioRxiv screening. These states are recorded in
`data/release/publication-readiness.json`.
