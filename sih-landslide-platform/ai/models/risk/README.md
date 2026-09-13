# Risk fusion model — extension point

`backend/app/services/risk/fusion.py` currently implements a documented,
interpretable weighted-logistic model (see WEIGHTS dict + docstring).

To upgrade to a trained model:

1. Build a labeled dataset: (feature bundle at time T) -> (landslide occurred
   within N days, Y/N), using `historical_landslides` + the same features
   `FeatureBundle` computes.
2. Train a LightGBM/XGBoost classifier; calibrate probabilities (Platt
   scaling / isotonic regression) — this is what makes "risk_probability" a
   genuinely calibrated probability rather than a logistic-squashed score.
3. Save the model artifact into `ai/models/risk/`.
4. Replace `services.risk.fusion.score()`'s body with
   `model.predict_proba(feature_vector)`, keeping the same return shape
   (`risk_score`, `risk_probability`, `normalized_features`, `contributions`).
5. Replace the linear `contributions` decomposition in
   `services/risk/explainability.py` with real SHAP values
   (`shap.TreeExplainer(model)`).

The API contract (`RiskAssessment` schema) does not need to change.
