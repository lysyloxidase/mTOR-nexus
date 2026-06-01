# Submission Checklist

Author: [`lysyloxidase`](https://github.com/lysyloxidase).

This checklist is intentionally fail-closed. An unchecked item blocks the
`v1.0.0` production tag.

- [x] Every generated figure has `figures/<n>/provenance.md` with source DOI,
  source-data commit SHA, and deterministic layout seed.
- [ ] Full pipeline runs in `<6h` on one A100 or `<18h` CPU-only on the
  independent production image.
- [ ] Submission-day DOI, UniProt, and PDB identifier link check is green.
- [x] AI model cards document all four Phase 6 components and limitations.
- [x] Selectivity training-set datasheet documents composition and limitations.
- [ ] Zenodo production DOI is minted and included in the Data Availability
  statement.
- [ ] Every author ORCID is present in `CITATION.cff`.
- [ ] Torin2 selectivity benchmark passes on validated weights.
- [ ] Complete verbatim Research Report caveats are supplied and imported.
- [x] All five nomenclature guards are enforced in CI-tested Python.
- [ ] Independent reproduction passes from the published Docker image alone.
- [x] Reviewer rebuttal kit contains at least seven anticipated comments.
- [ ] bioRxiv preprint is live, cross-references the repository, and is queued
  for a metadata update with the minted Zenodo DOI.
- [ ] Lighthouse performance is `>=90` and accessibility is `>=95` across all
  configured route families on the release image.

## Target Journals

Primary targets: Nature Reviews Drug Discovery, Cell Chemical Biology, or
Journal of Medicinal Chemistry. Companion methods targets: Bioinformatics or
Journal of Cheminformatics. Journal selection remains an author decision.
