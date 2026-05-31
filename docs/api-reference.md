# API Reference

The Phase 1 FastAPI service exposes:

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Readiness check and package version |
| `GET` | `/graph` | Curated normalized seed graph |

Run the development service with:

```bash
uv run uvicorn mtor_nexus.api.main:app --reload
```
