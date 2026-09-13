"""Uncertainty estimation.

Real, simple, documented approach appropriate for a rule-based fusion model:
uncertainty is driven by (a) how much of the input feature set is actually
available/live vs missing/demo, and (b) how close the weighted sum sits to
the decision boundary (0.5), where small input changes flip the category.

This is NOT a Monte Carlo dropout / ensemble-variance estimate (that needs a
trained neural or ensemble model — see ai/uncertainty/ for the scaffold to
extend this once a trained model exists). We are explicit about that so the
number is never over-claimed as more rigorous than it is.
"""


def estimate_uncertainty(normalized_features: dict[str, float], missing_feature_count: int,
                          total_feature_count: int, weighted_sum: float) -> dict:
    completeness = 1 - (missing_feature_count / max(total_feature_count, 1))
    boundary_distance = abs(weighted_sum - 0.5)  # 0 at the boundary, up to ~0.5 far from it
    boundary_confidence = min(1.0, boundary_distance * 2)

    confidence = round(0.5 * completeness + 0.5 * boundary_confidence, 3)
    uncertainty = round(1 - confidence, 3)

    return {
        "confidence": max(0.05, min(0.98, confidence)),
        "uncertainty": max(0.02, min(0.95, uncertainty)),
        "data_completeness": round(completeness, 3),
        "basis": "feature-completeness + decision-boundary distance (rule-based model; "
                 "not an ensemble/MC-dropout estimate — see ai/uncertainty/README.md)",
    }
