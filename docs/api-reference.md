# API Reference

The FastAPI service exposes:

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Readiness check and package version |
| `GET` | `/graph` | Curated normalized Phase 2 pathway graph |
| `GET` | `/diseases` | Phase 4 disease, association, and mutation overlay |
| `GET` | `/drugs` | Phase 5 inhibitor, target-link, structure, and ChEMBL bioactivity overlay |
| `GET` | `/ai/status` | Phase 6 readiness audit and locked scientific gates |
| `POST` | `/ai/predict` | Refusal-bound selectivity, resistance, and optional cofolding triage |
| `GET` | `/ai/scaffolds?limit=3` | Red-tagged computational-only scaffold hypotheses |

`POST /ai/predict` accepts:

```json
{
  "smiles": "CC1=CC=C(C=C1)C",
  "binding_mode": "atp_competitive",
  "include_cofolding": true
}
```

The Phase 6 prerelease intentionally returns no numerical pIC50 values. Queries
outside the Morgan-fingerprint domain are refused explicitly; in-domain
queries are refused until a trained artifact passes the locked gates.

Run the development service with:

```bash
uv run uvicorn mtor_nexus.api.main:app --reload
```
