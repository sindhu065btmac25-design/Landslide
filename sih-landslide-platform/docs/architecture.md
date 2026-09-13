# Architecture — NER Landslide Risk Intelligence Platform

## 1. Scope of this build

This repository is a **working, extensible scaffold**, not a finished production
deployment. It is built so that:

- Every external integration (Open-Meteo, Copernicus/Sentinel Hub, OSM/Overpass,
  DEM sources) has a real adapter class with the real HTTP call implemented.
- If credentials/network are unavailable at runtime, the adapter returns a
  structured `DataSourceUnavailable` result — it never fabricates a live reading.
- A separate, clearly-labeled **DEMO_MODE** provider set exists for
  demonstrations (judges, offline dev) using deterministic seeded data, per the
  project's own non-negotiable requirement that live and demo data must never
  be mixed silently.
- The risk engine is a real, explainable weighted/logistic fusion model over
  named features (not random numbers), with a documented path to swap in a
  trained LightGBM/XGBoost model (`ai/models/risk/`) without changing the API
  contract.

## 2. High-level architecture

```
FRONTEND (Next.js + TypeScript + MapLibre GL)
        |  REST + WebSocket
BACKEND (FastAPI)
   ├── api/routes        → HTTP surface, typed Pydantic I/O
   ├── services/          → one package per data domain (adapter pattern)
   │     weather/          Open-Meteo adapter (real) + demo provider
   │     satellite/        Copernicus/Sentinel Hub adapter (real) + demo
   │     terrain/          DEM-derived slope/aspect/ruggedness
   │     historical/       GeoJSON/CSV ingestion of past landslide events
   │     infrastructure/   OSM/Overpass adapter (real) + demo
   │     risk/             fusion risk engine + explainability + uncertainty
   │     impact/           spatial intersection: risk × infrastructure
   │     decision/         risk+uncertainty+exposure → recommended actions
   │     alerts/           threshold-crossing, dedup, cooldown
   │     feedback/         human-in-the-loop feedback storage
   ├── workers/            Celery-shaped scheduled jobs (ingest_*, update_risk)
   └── db/                 SQLAlchemy models mapped to PostGIS schema
AI (ai/)
   ├── features/           per-modality feature builders
   ├── models/risk/         fusion model wrapper (rule-based now, LightGBM-ready)
   ├── models/segmentation/ U-Net scaffold + "checkpoint unavailable" health state
   ├── explainability/      SHAP-ready driver decomposition
   └── uncertainty/         ensemble-variance / confidence estimator
DB: PostgreSQL + PostGIS (docker-compose service)
CACHE/QUEUE: Redis
```

## 3. Data source honesty contract

Every adapter returns an envelope:

```json
{
  "status": "live" | "demo" | "unavailable",
  "source": "open-meteo",
  "observed_at": "...",
  "ingested_at": "...",
  "data": {...} | null,
  "message": "optional human-readable reason"
}
```

The frontend renders a `LIVE / DEMO / DEGRADED / OFFLINE` badge per layer
directly from this envelope — never inferred.

## 4. What's implemented at "real integration" depth vs "scaffold" depth

| Component | Depth |
|---|---|
| Open-Meteo weather adapter | Real HTTP client, real response parsing |
| Risk fusion engine (rule-based, explainable) | Real, deterministic, documented weights |
| Uncertainty estimator (feature-completeness based) | Real, simple, documented |
| Decision engine | Real rule table from the spec's section 14 |
| Impact engine (shapely-based intersection) | Real, works on demo infra data |
| Alerting (threshold + cooldown + dedup) | Real |
| Copernicus/Sentinel Hub satellite adapter | Real HTTP client shape; requires client ID/secret to go live |
| OSM/Overpass infrastructure adapter | Real HTTP client shape; requires network |
| DEM/terrain adapter | Real interface; ships with demo NER terrain samples |
| Segmentation U-Net | Real PyTorch module definition; no trained checkpoint shipped (reports `checkpoint_unavailable`, per spec §12) |
| Celery workers | Real task definitions; wired to run under `celery -A app.workers.celery_app` |
| Frontend map/dashboard | Real Next.js app, live-fetches backend, demo mode banner |

## 5. Roadmap beyond this scaffold

1. Obtain Copernicus Data Space + NASA GPM credentials, flip `.env` to live.
2. Collect/label a NER historical landslide dataset; train segmentation
   checkpoint; drop into `ai/models/segmentation/checkpoints/`.
3. Train the LightGBM fusion model on labeled risk outcomes; swap
   `ai/models/risk/fusion.py`'s rule-based scorer for the trained model artifact.
4. Stand up PostGIS with real spatial indexes and load real NER OSM extracts.
5. Add auth (JWT) in front of `/api/v1/feedback` and admin routes.
