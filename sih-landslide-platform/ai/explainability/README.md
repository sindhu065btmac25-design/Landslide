SHAP-based explainability for a trained fusion model belongs here once one
exists (see `ai/models/risk/README.md`). The current rule-based model's
explainability lives in `backend/app/services/risk/explainability.py` since
it's an exact linear decomposition, not an approximation — no SHAP needed yet.
