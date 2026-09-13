from fastapi import APIRouter

from core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready():
    return {"status": "ready"}


@router.get("/data-sources/status")
async def data_sources_status():
    settings = get_settings()
    return {
        "demo_mode": settings.DEMO_MODE,
        "sources": {
            "open-meteo": "configured (no key required)",
            "sentinel-hub": "configured" if settings.COPERNICUS_CLIENT_ID else "missing credentials — DEMO fallback active",
            "overpass-osm": "configured (no key required, network-dependent)",
            "historical-events": "see /data/raw/historical",
        },
    }
