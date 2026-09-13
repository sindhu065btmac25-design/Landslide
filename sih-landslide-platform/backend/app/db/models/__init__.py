"""SQLAlchemy + GeoAlchemy2 models mapping to the PostGIS schema described in
docs/architecture.md. Not auto-migrated in this scaffold (no Alembic wired
up yet) — see scripts/init_db.sql for a directly-runnable DDL equivalent.
"""
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Float, Integer, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class WeatherObservation(Base):
    __tablename__ = "weather_observations"
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
    source = Column(String, nullable=False)
    observed_at = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    payload = Column(JSON)


class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POLYGON", srid=4326))
    collection = Column(String, nullable=False)
    observed_at = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    cloud_cover_pct = Column(Float)
    payload = Column(JSON)


class HistoricalLandslide(Base):
    __tablename__ = "historical_landslides"
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
    event_date = Column(DateTime)
    source = Column(String)
    confidence = Column(Float, nullable=True)


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"
    id = Column(Integer, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
    risk_score = Column(Float, nullable=False)
    risk_probability = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    confidence = Column(Float)
    uncertainty = Column(Float)
    model_version = Column(String)
    feature_version = Column(String)
    drivers = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class InfrastructureAssetModel(Base):
    __tablename__ = "infrastructure_assets"
    id = Column(String, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
    asset_type = Column(String, nullable=False)
    name = Column(String, nullable=True)
    estimated_population = Column(Integer, nullable=True)


class AlertModel(Base):
    __tablename__ = "alerts"
    id = Column(String, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
    severity = Column(String, nullable=False)
    previous_category = Column(String, nullable=True)
    new_category = Column(String, nullable=False)
    reasons = Column(JSON)
    affected_assets = Column(JSON)
    recommended_actions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(String, primary_key=True)
    geom = Column(Geometry("POINT", srid=4326))
    feedback_type = Column(String, nullable=False)
    related_risk_assessment_id = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    submitted_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String)
    records_processed = Column(Integer, default=0)
    error = Column(String, nullable=True)
