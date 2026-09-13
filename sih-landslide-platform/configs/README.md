Environment-specific config overlays (e.g. per-deployment risk thresholds,
alert cooldowns) can live here as YAML/JSON, loaded by
`backend/app/core/config.py`. Empty in this scaffold — thresholds currently
live directly in `Settings`.
