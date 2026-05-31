# AI Model Cards

No predictive model ships in Phase 1. Every future model must add a model card
before deployment.

## Required fields

- Model name, version, owner, and release date
- Intended use and out-of-scope use
- Training, validation, and test datasets with provenance
- Species and experimental-context coverage
- Evaluation metrics and uncertainty reporting
- Known limitations, failure modes, and bias analysis
- Reproducibility instructions and artifact digest
- Human-review requirements

AI-predicted graph edges must use tier `speculative` and species flag
`computational` until experimental evidence is curated.
