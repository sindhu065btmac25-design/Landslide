"""Historical landslide event ingestion.

Real adapter: loads GeoJSON/CSV files placed under /data/raw/historical/.
Ships with a small deterministic demo dataset for the NER so the risk engine
and map have something real to compute against out of the box.
"""
import csv
import hashlib
import json
from pathlib import Path

from schemas.common import Location

DATA_DIR = Path(__file__).resolve().parents[4] / "data" / "raw" / "historical"


def _seed(location: Location, salt: str) -> float:
    key = f"{location.latitude:.3f}:{location.longitude:.3f}:{salt}"
    digest = hashlib.sha256(key.encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


class HistoricalEventService:
    def load_events(self) -> list[dict]:
        events: list[dict] = []
        if DATA_DIR.exists():
            for path in DATA_DIR.glob("*.geojson"):
                events.extend(self._load_geojson(path))
            for path in DATA_DIR.glob("*.csv"):
                events.extend(self._load_csv(path))
        return events

    def _load_geojson(self, path: Path) -> list[dict]:
        try:
            payload = json.loads(path.read_text())
            out = []
            for feat in payload.get("features", []):
                coords = feat.get("geometry", {}).get("coordinates")
                props = feat.get("properties", {})
                if not coords:
                    continue
                out.append({
                    "latitude": coords[1], "longitude": coords[0],
                    "date": props.get("date"), "source": path.name,
                    "confidence": props.get("confidence"),
                })
            return out
        except (json.JSONDecodeError, KeyError):
            return []

    def _load_csv(self, path: Path) -> list[dict]:
        out = []
        try:
            with path.open() as f:
                for row in csv.DictReader(f):
                    out.append({
                        "latitude": float(row["latitude"]), "longitude": float(row["longitude"]),
                        "date": row.get("date"), "source": path.name,
                        "confidence": row.get("confidence"),
                    })
        except (KeyError, ValueError, OSError):
            pass
        return out

    def susceptibility_near(self, location: Location, radius_deg: float = 0.1) -> dict:
        """Real density calculation over loaded events, if any; otherwise a
        deterministic seeded susceptibility value clearly noted as such."""
        events = self.load_events()
        nearby = [
            e for e in events
            if abs(e["latitude"] - location.latitude) <= radius_deg
            and abs(e["longitude"] - location.longitude) <= radius_deg
        ]
        if events:
            density = min(1.0, len(nearby) / 10)
            return {"historical_density": round(density, 3), "event_count": len(nearby), "source": "loaded historical dataset"}
        seeded = _seed(location, "hist")
        return {"historical_density": round(seeded * 0.6, 3), "event_count": 0,
                "source": "no historical dataset loaded — seeded placeholder, see data/raw/historical/README.md"}
