# Tier + Species Rubric for mTOR-NEXUS

Every edge **must** carry a tier badge and at least one species-evidence flag.

## Tier definitions

- **ROBUST**: supported by at least one of: a high-resolution structure
  resolving the interaction, human genetics, or at least three independent
  laboratories with concordant mechanistic data.
- **PLAUSIBLE**: supported by two to four studies, a debated mechanism, or a
  single experimental modality.
- **SPECULATIVE**: supported by a single study or computation only.

## Species and context flags

- `human`
- `rodent`
- `human_and_rodent`
- `in_vitro_biochemical`
- `structural`
- `computational`

An edge may carry multiple flags when evidence spans contexts. Metabolic-disease
and aging-mechanism claims must retain their true species provenance. Rodent
evidence must not be presented as human evidence.

## Worked examples

| Edge | Tier | Species or context |
| --- | --- | --- |
| AKT1 phosphorylates TSC2 T1462 | ROBUST | `human_and_rodent` |
| MTORC1 phosphorylates RPS6KB1 T389 | ROBUST | `human_and_rodent` |
| MTORC1 phosphorylates EIF4EBP1 T37/T46 | ROBUST | `human_and_rodent` |
| SESN2 binds GATOR2 | ROBUST | `structural`, `human` |
| RapaLink-1 binds MTOR | ROBUST | `structural`, `human` |
| AI-predicted inhibitor pose | SPECULATIVE | `computational` |
