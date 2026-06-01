# API Reference

The Phase 1 FastAPI service exposes:

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Readiness check and package version |
| `GET` | `/graph` | Curated normalized Phase 2 pathway graph |
| `GET` | `/diseases` | Phase 4 disease, association, and mutation overlay |
| `GET` | `/drugs` | Phase 5 inhibitor, target-link, structure, and ChEMBL bioactivity overlay |

Run the development service with:

```bash
uv run uvicorn mtor_nexus.api.main:app --reload
```
