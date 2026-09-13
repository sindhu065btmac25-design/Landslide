"""Real Overpass (OpenStreetMap) adapter.

Queries roads, bridges, settlements, hospitals and schools within a radius of
a point. Falls back to a labeled demo asset set if the network call fails.
"""
from datetime import datetime, timezone

import httpx

from core.config import get_settings
from schemas.common import DataStatus, Location, SourceEnvelope
from schemas.domain import AssetType, InfrastructureAsset, InfrastructureResponse

OVERPASS_QUERY_TEMPLATE = """
[out:json][timeout:25];
(
  way["highway"](around:{radius},{lat},{lon});
  way["bridge"="yes"](around:{radius},{lat},{lon});
  node["amenity"="hospital"](around:{radius},{lat},{lon});
  node["amenity"="school"](around:{radius},{lat},{lon});
  node["place"~"village|town|hamlet"](around:{radius},{lat},{lon});
);
out center;
"""


class OverpassAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def fetch_assets(self, location: Location, radius_m: int = 5000) -> InfrastructureResponse:
        now = datetime.now(timezone.utc)
        query = OVERPASS_QUERY_TEMPLATE.format(
            radius=radius_m, lat=location.latitude, lon=location.longitude
        )
        try:
            async with httpx.AsyncClient(timeout=self.settings.HTTP_TIMEOUT_SECONDS) as client:
                resp = await client.post(self.settings.OVERPASS_BASE_URL, data={"data": query})
                resp.raise_for_status()
                payload = resp.json()
            assets = self._parse(payload)
            envelope = SourceEnvelope(status=DataStatus.LIVE, source="overpass-osm", ingested_at=now)
            return InfrastructureResponse(envelope=envelope, assets=assets)
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            envelope = SourceEnvelope(
                status=DataStatus.UNAVAILABLE,
                source="overpass-osm",
                ingested_at=now,
                message=f"Overpass fetch failed: {exc.__class__.__name__}: {exc}",
            )
            return InfrastructureResponse(envelope=envelope, assets=[])

    def _parse(self, payload: dict) -> list[InfrastructureAsset]:
        assets: list[InfrastructureAsset] = []
        for el in payload.get("elements", []):
            tags = el.get("tags", {})
            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if lat is None or lon is None:
                continue
            if tags.get("amenity") == "hospital":
                asset_type = AssetType.HOSPITAL
            elif tags.get("amenity") == "school":
                asset_type = AssetType.SCHOOL
            elif tags.get("bridge") == "yes":
                asset_type = AssetType.BRIDGE
            elif "place" in tags:
                asset_type = AssetType.SETTLEMENT
            elif "highway" in tags:
                asset_type = AssetType.ROAD
            else:
                continue
            assets.append(
                InfrastructureAsset(
                    id=str(el.get("id")),
                    type=asset_type,
                    name=tags.get("name"),
                    latitude=lat,
                    longitude=lon,
                )
            )
        return assets
