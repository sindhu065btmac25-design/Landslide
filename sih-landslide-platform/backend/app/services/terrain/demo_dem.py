"""Deterministic terrain provider.

Real integration point: Copernicus DEM / SRTM via a raster read (rasterio) at
(lat, lon). That requires downloading/hosting DEM tiles, which needs network
and disk we don't have in this environment — so this ships a documented,
seeded terrain generator standing in for the real DEM query, behind the same
adapter interface (`TerrainAdapter.get_terrain`), so swapping in rasterio-based
real reads later is a one-file change.
"""
import hashlib

from app.schemas.common import Location


def _seed(location: Location, salt: str) -> float:
    key = f"{location.latitude:.3f}:{location.longitude:.3f}:{salt}"
    digest = hashlib.sha256(key.encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def get_terrain_features(location: Location) -> dict:
    slope = round(5 + _seed(location, "slope") * 45, 1)  # degrees
    elevation = round(100 + _seed(location, "elev") * 2400, 1)  # meters, NER range
    aspect = round(_seed(location, "aspect") * 360, 1)
    ruggedness = round(_seed(location, "rugged") * 10, 2)
    return {
        "slope_deg": slope,
        "elevation_m": elevation,
        "aspect_deg": aspect,
        "terrain_ruggedness_index": ruggedness,
        "source": "demo-dem-generator (Copernicus DEM adapter interface, not yet credentialed)",
    }

