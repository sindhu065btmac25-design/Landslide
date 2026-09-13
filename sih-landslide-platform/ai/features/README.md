Per-modality feature-builder modules (weather/terrain/satellite/historical/
infrastructure feature engineering) live here once they grow beyond the
inline computation currently in `backend/app/services/risk/engine.py`
(`FeatureBundle` construction). Kept inline for now since the scaffold's
feature set is still small — split out here as it grows.
