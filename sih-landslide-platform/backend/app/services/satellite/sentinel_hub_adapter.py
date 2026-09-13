"""Real Sentinel Hub / Copernicus Data Space adapter shape.

Sentinel Hub requires OAuth2 client-credentials auth. This adapter implements
the real token exchange and catalog search calls; it will go LIVE the moment
COPERNICUS_CLIENT_ID / COPERNICUS_CLIENT_SECRET are set and network is
available. Without credentials it deterministically reports UNAVAILABLE
(never fabricated imagery), matching §4/§33 of the spec.
"""
from datetime import datetime, timezone

import httpx

from app.core.config import get_settings
from app.schemas.common import DataStatus, Location, SourceEnvelope

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


class SentinelHubAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.settings.COPERNICUS_CLIENT_ID,
                "client_secret": self.settings.COPERNICUS_CLIENT_SECRET,
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    async def find_latest_acquisition(
        self, location: Location, collection: str = "sentinel-2-l2a", max_cloud_pct: int = 30
    ) -> dict:
        now = datetime.now(timezone.utc)
        if not self.settings.COPERNICUS_CLIENT_ID or not self.settings.COPERNICUS_CLIENT_SECRET:
            return {
                "envelope": SourceEnvelope(
                    status=DataStatus.UNAVAILABLE,
                    source=f"sentinel-hub:{collection}",
                    ingested_at=now,
                    message="COPERNICUS_CLIENT_ID/SECRET not configured — cannot authenticate.",
                ),
                "acquisition": None,
            }
        try:
            async with httpx.AsyncClient(timeout=self.settings.HTTP_TIMEOUT_SECONDS) as client:
                token = await self._get_token(client)
                search_url = f"{self.settings.SENTINEL_HUB_BASE_URL}/api/v1/catalog/1.0.0/search"
                bbox = [
                    location.longitude - 0.05, location.latitude - 0.05,
                    location.longitude + 0.05, location.latitude + 0.05,
                ]
                resp = await client.post(
                    search_url,
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "collections": [collection],
                        "bbox": bbox,
                        "limit": 1,
                        "query": {"eo:cloud_cover": {"lt": max_cloud_pct}},
                        "sortby": [{"field": "properties.datetime", "direction": "desc"}],
                    },
                )
                resp.raise_for_status()
                features = resp.json().get("features", [])
                if not features:
                    return {
                        "envelope": SourceEnvelope(
                            status=DataStatus.UNAVAILABLE, source=f"sentinel-hub:{collection}",
                            ingested_at=now, message="No suitable low-cloud acquisition found.",
                        ),
                        "acquisition": None,
                    }
                feat = features[0]
                observed_at = feat.get("properties", {}).get("datetime")
                return {
                    "envelope": SourceEnvelope(
                        status=DataStatus.LIVE, source=f"sentinel-hub:{collection}",
                        observed_at=observed_at, ingested_at=now,
                        message="Near-real-time observation, not instant real-time (see §4).",
                    ),
                    "acquisition": feat,
                }
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            return {
                "envelope": SourceEnvelope(
                    status=DataStatus.UNAVAILABLE, source=f"sentinel-hub:{collection}",
                    ingested_at=now, message=f"Sentinel Hub call failed: {exc.__class__.__name__}: {exc}",
                ),
                "acquisition": None,
            }

