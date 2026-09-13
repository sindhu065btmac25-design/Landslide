"""Explainability: turns fusion.score()'s `contributions` dict into ranked,
human-readable RiskDriver entries. Generated from actual model features only
— no invented narrative (§9 requirement).

For the current rule-based fusion model, "contribution" is the feature's
normalized value times its documented weight, which is an exact, honest
decomposition of the weighted sum (unlike SHAP, no approximation needed
because the model IS linear-in-features until the logistic squash). If/when
`ai/models/risk/fusion.py` is replaced by a trained LightGBM model, this
module's interface is unchanged — only where `contributions` comes from
changes (real SHAP values instead of linear terms).
"""
from app.schemas.risk import RiskDriver

FACTOR_LABELS = {
    "rainfall_24h": "24h rainfall",
    "rainfall_72h": "72h antecedent rainfall",
    "soil_moisture": "Soil moisture",
    "slope": "Slope steepness",
    "ruggedness": "Terrain ruggedness",
    "ndvi_change": "Vegetation loss (NDVI change)",
    "sar_change": "SAR surface change",
    "historical_density": "Historical landslide density",
}


def build_drivers(contributions: dict[str, float], normalized: dict[str, float]) -> list[RiskDriver]:
    total = sum(abs(v) for v in contributions.values()) or 1.0
    ranked = sorted(contributions.items(), key=lambda kv: abs(kv[1]), reverse=True)
    drivers = []
    for factor, contribution in ranked:
        drivers.append(
            RiskDriver(
                factor=FACTOR_LABELS.get(factor, factor),
                contribution=round(contribution / total, 3),
                value=round(normalized.get(factor, 0.0), 3),
            )
        )
    return drivers

