# AI-Powered Landslide Risk Intelligence Platform — NER, India

SIH prototype: predict → explain → quantify uncertainty → assess impact →
recommend action → learn, for landslide risk across India's North Eastern
Region.

**Read `docs/architecture.md` first.** It explains exactly which parts of this
system are real, credentialed integrations vs. clearly-labeled DEMO fallbacks,
and what's needed to take each part further. This is a working scaffold, not
a finished production deployment — see "Honest scope" below.

## Honest scope

- This was built in a sandboxed environment with **no network access**, so
  the pip/npm installs and end-to-end boot below have **not been run by the
  builder**. All Python source passed `py_compile`, and the core risk-fusion
  logic was unit-verified standalone (see `backend/tests/`). You should
  expect to fix minor integration issues (a missing import, a version pin) on
  first run — treat this as a strong, correctly-architected starting point,
  not a guaranteed zero-friction boot.
- `DEMO_MODE=true` by default. Every demo value is clearly labeled `DEMO` in
  API responses and the UI — never presented as a live observation.
- Satellite (Sentinel Hub) and full OSM infrastructure require your own free
  credentials/network to go LIVE — see `.env.example`.
- No trained ML checkpoints ship with this repo (segmentation U-Net, risk
  fusion model). The rule-based fusion engine is real and explainable, but is
  not a substitute for a model trained on labeled ground-truth landslide data.
  See `ai/models/risk/README.md` and `ai/models/segmentation/checkpoints/README.md`
  for exactly how to add them.

## Quick start (Docker — recommended)

```bash
cp .env.example .env
docker compose up --build
```

- Backend API: http://localhost:8000 (docs at `/docs`)
- Frontend dashboard: http://localhost:3000
- Postgres/PostGIS: localhost:5432 (auto-runs `scripts/init_db.sql`)
- Redis: localhost:6379

## Quick start (local, without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
cd app
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API docs.

Run tests:

```bash
cd backend
pytest
```

### Background worker (optional — requires Redis running)

```bash
cd backend/app
celery -A workers.celery_app worker --beat --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit http://localhost:3000.

### Database (optional, for persistence beyond in-memory demo state)

```bash
# with a local Postgres+PostGIS instance running:
psql -U postgres -d landslide -f scripts/init_db.sql
```

## Going from DEMO to LIVE

1. Register at https://dataspace.copernicus.eu/ for `COPERNICUS_CLIENT_ID` /
   `COPERNICUS_CLIENT_SECRET`, put them in `.env`.
2. Set `DEMO_MODE=false` in `.env`.
3. Restart the backend. Each data layer (weather/satellite/infrastructure)
   will now attempt its real provider first and only fall back to a clearly
   labeled DEMO reading if that specific provider is unreachable — never
   silently.

## Repository structure

```
backend/   FastAPI app — routes, services (adapters), risk engine, workers, tests
frontend/  Next.js + MapLibre "Mission Control" dashboard
ai/        Model definitions (fusion, segmentation), explainability, uncertainty
data/      raw/processed/cache — drop real historical event files under data/raw/historical
docs/      architecture.md — read this first
scripts/   init_db.sql — PostGIS schema
docker-compose.yml, .env.example
```

## API surface

See `/docs` (Swagger) once the backend is running, or `docs/architecture.md`
§ API design. Key endpoints:

- `GET /api/v1/risk/location/{lat}/{lon}` — full explainable risk assessment
- `GET /api/v1/risk/grid` — coarse sampled NER risk grid
- `GET /api/v1/weather/current`, `/api/v1/satellite/latest`, `/api/v1/terrain`,
  `/api/v1/infrastructure`
- `GET /api/v1/alerts` — threshold-crossing alert check for a location
- `POST /api/v1/feedback` — human feedback loop
- `GET /api/v1/analytics/timeseries`
- `WS /ws/risk` — live-streamed risk updates for a location
- `GET /data-sources/status` — which providers are LIVE vs DEMO right now

## License / attribution

Built for Smart India Hackathon demonstration purposes. Uses Open-Meteo
(no key required), OpenStreetMap/Overpass data (© OpenStreetMap
contributors), and is designed to integrate Copernicus Sentinel data
(© Copernicus Programme) once credentialed.
