# Uncertainty estimation — extension point

The scaffold's live uncertainty estimate
(`backend/app/services/risk/uncertainty.py`) uses feature-completeness and
decision-boundary distance, appropriate for the current rule-based fusion
model.

Once a trained neural or ensemble fusion model exists, replace it with one of:

- **Ensemble variance**: train k models (bagging/different seeds), report
  prediction std-dev as uncertainty.
- **Monte Carlo dropout**: keep dropout active at inference, run N stochastic
  forward passes, use output variance.
- **Conformal prediction**: wrap the trained model to produce calibrated
  prediction intervals with coverage guarantees.

Keep the same output contract: `{confidence: float, uncertainty: float}` so
`RiskAssessment` and the frontend don't need to change.
