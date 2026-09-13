"use client";

import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { api } from "../lib/api";
import type { RiskAssessment } from "../types/api";

const NER_CENTERS = [
  { name: "Guwahati, Assam", lat: 26.14, lon: 91.73 },
  { name: "Shillong, Meghalaya", lat: 25.57, lon: 91.88 },
  { name: "Itanagar, Arunachal Pradesh", lat: 27.08, lon: 93.62 },
  { name: "Imphal, Manipur", lat: 24.82, lon: 93.94 },
  { name: "Aizawl, Mizoram", lat: 23.73, lon: 92.72 },
  { name: "Kohima, Nagaland", lat: 25.67, lon: 94.11 },
  { name: "Agartala, Tripura", lat: 23.83, lon: 91.28 },
  { name: "Gangtok, Sikkim", lat: 27.33, lon: 88.61 },
];

function Badge({ status }: { status: string }) {
  const cls = `badge badge-${status}`;
  const label = status === "live" ? "LIVE" : status === "demo" ? "DEMO" : status.toUpperCase();
  return <span className={cls}>● {label}</span>;
}

export default function Dashboard() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const [selected, setSelected] = useState(NER_CENTERS[0]);
  const [assessment, setAssessment] = useState<RiskAssessment | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [demoMode, setDemoMode] = useState<boolean | null>(null);

  useEffect(() => {
    if (mapRef.current || !mapContainer.current) return;
    mapRef.current = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: [92.5, 26],
      zoom: 5.2,
    });
    NER_CENTERS.forEach((c) => {
      const marker = new maplibregl.Marker({ color: "#3ba7ff" })
        .setLngLat([c.lon, c.lat])
        .setPopup(new maplibregl.Popup().setText(c.name))
        .addTo(mapRef.current!);
      marker.getElement().addEventListener("click", () => setSelected(c));
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .dataSourceStatus()
      .then((s: any) => !cancelled && setDemoMode(s.demo_mode))
      .catch(() => {});
    (api.risk(selected.lat, selected.lon, selected.name) as Promise<RiskAssessment>)
      .then((data) => !cancelled && setAssessment(data))
      .catch((e) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [selected]);

  return (
    <>
      <header className="header">
        <div className="title">🏔️ NER Landslide Intelligence — Mission Control</div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          {demoMode !== null && (
            <Badge status={demoMode ? "demo" : "live"} />
          )}
          <span className="muted">
            {assessment ? `Last update: ${new Date(assessment.timestamp).toLocaleTimeString()}` : "—"}
          </span>
        </div>
      </header>
      <div className="layout">
        <nav className="sidebar">
          <div className="muted" style={{ marginBottom: 8, paddingLeft: 10 }}>DISTRICTS</div>
          {NER_CENTERS.map((c) => (
            <a
              key={c.name}
              className={c.name === selected.name ? "active" : ""}
              onClick={() => setSelected(c)}
              style={{ cursor: "pointer" }}
            >
              {c.name}
            </a>
          ))}
        </nav>

        <div className="map-wrap">
          <div ref={mapContainer} style={{ width: "100%", height: "100%" }} />
        </div>

        <aside className="panel">
          {error && <div className="card">⚠️ {error}</div>}
          {loading && !assessment && <div className="card">Loading risk assessment…</div>}
          {assessment && (
            <>
              <div className="card">
                <div className="muted">{selected.name}</div>
                <div className="risk-score">{assessment.risk_score.toFixed(0)}</div>
                <span className={`category-pill cat-${assessment.category}`}>{assessment.category.replace("_", " ")}</span>
                <div style={{ marginTop: 10 }} className="muted">
                  Probability {Math.round(assessment.risk_probability * 100)}% · Confidence{" "}
                  {Math.round(assessment.confidence * 100)}% · Uncertainty ±
                  {Math.round(assessment.uncertainty * 100)}%
                </div>
                {assessment.trend_explanation && (
                  <div className="muted" style={{ marginTop: 8 }}>{assessment.trend_explanation}</div>
                )}
              </div>

              <div className="card">
                <div style={{ marginBottom: 10, fontWeight: 600 }}>Top Risk Drivers</div>
                {assessment.drivers.slice(0, 6).map((d) => (
                  <div className="driver-row" key={d.factor}>
                    <div style={{ width: 140 }}>{d.factor}</div>
                    <div className="driver-bar-bg">
                      <div className="driver-bar" style={{ width: `${Math.min(100, Math.abs(d.contribution) * 100 * 2)}%` }} />
                    </div>
                    <div className="muted">{Math.round(Math.abs(d.contribution) * 100)}%</div>
                  </div>
                ))}
              </div>

              <div className="card">
                <div style={{ marginBottom: 10, fontWeight: 600 }}>Data Freshness</div>
                {assessment.data_freshness.map((f) => (
                  <div key={f.layer} style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 6 }}>
                    <span>{f.layer}</span>
                    <Badge status={f.status} />
                  </div>
                ))}
                <div className="muted" style={{ marginTop: 6 }}>
                  Model {assessment.model_version} · Features {assessment.feature_version}
                </div>
              </div>
            </>
          )}
        </aside>
      </div>
    </>
  );
}
