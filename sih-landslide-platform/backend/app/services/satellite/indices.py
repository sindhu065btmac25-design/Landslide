"""Spectral index calculations from band arrays (NumPy).

Real math, operates on whatever band arrays are supplied — by the live
Sentinel Hub adapter once credentialed, or by demo band arrays in the
meantime. This module has no knowledge of where the bands came from.
"""
import numpy as np


def ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    return _safe_ratio(nir - red, nir + red)


def ndwi(nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
    return _safe_ratio(nir - swir, nir + swir)


def nbr(nir: np.ndarray, swir2: np.ndarray) -> np.ndarray:
    return _safe_ratio(nir - swir2, nir + swir2)


def vv_vh_ratio(vv: np.ndarray, vh: np.ndarray) -> np.ndarray:
    return _safe_ratio(vv, vh, additive=False)


def change_score(pre: np.ndarray, post: np.ndarray) -> float:
    """Mean absolute normalized change between two index rasters, 0..1."""
    diff = np.abs(post - pre)
    return float(np.clip(np.nanmean(diff), 0, 1))


def _safe_ratio(numerator: np.ndarray, denominator: np.ndarray, additive: bool = True) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(denominator != 0, numerator / denominator, 0.0)
    return result if additive else np.clip(result, 0, 10)
