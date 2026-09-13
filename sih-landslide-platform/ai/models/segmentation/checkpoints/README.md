Trained checkpoints (e.g. `unet_landslide.pt`) go here. None are shipped —
train on a labeled NER landslide segmentation dataset (see docs/architecture.md
roadmap). Until then `SegmentationInference.health()` reports
`checkpoint_unavailable` and the API surfaces that status rather than a
fabricated mask.
