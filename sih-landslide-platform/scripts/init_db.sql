-- Run against the postgres service once (docker-compose exec postgres psql ...)
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS weather_observations (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(POINT, 4326),
    source TEXT NOT NULL,
    observed_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ DEFAULT now(),
    payload JSONB
);
CREATE INDEX IF NOT EXISTS idx_weather_geom ON weather_observations USING GIST (geom);

CREATE TABLE IF NOT EXISTS risk_predictions (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(POINT, 4326),
    risk_score DOUBLE PRECISION NOT NULL,
    risk_probability DOUBLE PRECISION NOT NULL,
    category TEXT NOT NULL,
    confidence DOUBLE PRECISION,
    uncertainty DOUBLE PRECISION,
    model_version TEXT,
    feature_version TEXT,
    drivers JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_risk_geom ON risk_predictions USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_risk_created ON risk_predictions (created_at);

CREATE TABLE IF NOT EXISTS historical_landslides (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(POINT, 4326),
    event_date DATE,
    source TEXT,
    confidence DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_hist_geom ON historical_landslides USING GIST (geom);

CREATE TABLE IF NOT EXISTS infrastructure_assets (
    id TEXT PRIMARY KEY,
    geom GEOMETRY(POINT, 4326),
    asset_type TEXT NOT NULL,
    name TEXT,
    estimated_population INT
);
CREATE INDEX IF NOT EXISTS idx_infra_geom ON infrastructure_assets USING GIST (geom);

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    geom GEOMETRY(POINT, 4326),
    severity TEXT NOT NULL,
    previous_category TEXT,
    new_category TEXT NOT NULL,
    reasons JSONB,
    affected_assets JSONB,
    recommended_actions JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS feedback (
    id TEXT PRIMARY KEY,
    geom GEOMETRY(POINT, 4326),
    feedback_type TEXT NOT NULL,
    related_risk_assessment_id TEXT,
    notes TEXT,
    submitted_by TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id SERIAL PRIMARY KEY,
    job_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    status TEXT,
    records_processed INT DEFAULT 0,
    error TEXT
);
