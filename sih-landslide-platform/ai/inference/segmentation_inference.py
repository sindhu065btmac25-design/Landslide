"""Inference wrapper with an honest model-health contract: if no checkpoint
is present, `.health()` reports checkpoint_unavailable and `.predict()`
raises rather than returning a fabricated mask."""
from pathlib import Path

import numpy as np
import torch

from models.segmentation.unet import LightUNet

CHECKPOINT_PATH = Path(__file__).resolve().parents[1] / "models" / "segmentation" / "checkpoints" / "unet_landslide.pt"


class SegmentationModelUnavailable(RuntimeError):
    pass


class SegmentationInference:
    def __init__(self):
        self.model: LightUNet | None = None
        self._load()

    def _load(self):
        if not CHECKPOINT_PATH.exists():
            self.model = None
            return
        model = LightUNet()
        state = torch.load(CHECKPOINT_PATH, map_location="cpu")
        model.load_state_dict(state)
        model.eval()
        self.model = model

    def health(self) -> dict:
        if self.model is None:
            return {"status": "checkpoint_unavailable", "checkpoint_path": str(CHECKPOINT_PATH)}
        return {"status": "ready", "checkpoint_path": str(CHECKPOINT_PATH)}

    def predict(self, bands: np.ndarray) -> np.ndarray:
        """bands: (4, H, W) float32 array, e.g. [B04, B08, B11, B12]."""
        if self.model is None:
            raise SegmentationModelUnavailable(
                "No trained segmentation checkpoint present at "
                f"{CHECKPOINT_PATH}. Train and drop a checkpoint before calling predict()."
            )
        tensor = torch.from_numpy(bands).unsqueeze(0).float()
        with torch.no_grad():
            mask = self.model(tensor)
        return mask.squeeze().numpy()
