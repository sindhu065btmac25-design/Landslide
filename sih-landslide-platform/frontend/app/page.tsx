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
  const label =
    status === "live"
      ? "LIVE"
      : status === "demo"
        ? "DEMO"
        : status.toUpperCase();

  return <span className={`badge badge-${status}`}>● {label}</span>;
}

function getAction(category: string) {
  switch (category) {
    case "CRITICAL":
      return {
        title: "Immediate emergency action",
        text: "Restrict access to vulnerable slopes and roads. Initiate evacuation readiness and field inspection.",
      };
    case "VERY_HIGH":
      return {
        title: "Urgent field inspection",
        text: "Inspect vulnerable slopes, roads and settlements. Prepare traffic restrictions and evacuation support.",
      };
    case "HIGH":
      return {
        title: "Enhanced monitoring",
        text: "Increase slope monitoring and inspect critical infrastructure. Keep local response teams ready.",
      };
    case "MODERATE":
      return {
        title: "Watch and monitor",
        text: "Continue rainfall and slope monitoring. Prioritize vulnerable roads and settlements for inspection.",
      };
    default:
      return {
        title: "Routine monitoring",
        text: "Continue normal monitoring. No immediate intervention is indicated by the current risk assessment.",
      };
  }
}
function getRiskColor(category: string) {
  switch (category) {
    case "CRITICAL":
      return "#7f1d1d";
    case "VERY_HIGH":
      return "#dc2626";
    case "HIGH":
      return "#f97316";
    case "MODERATE":
      return "#eab308";
    default:
      return "#22c55e";
  }
}
export default function Dashboard() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const infrastructureMarkersRef = useRef<maplibregl.Marker[]>([]);

  const [selected, setSelected] = useState(NER_CENTERS[0]);
  const [assessment, setAssessment] = useState<RiskAssessment | null>(null);
  const [weather, setWeather] = useState<any>(null);
  const [alerts, setAlerts] = useState<any>(null);
  const [infrastructure, setInfrastructure] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mapReady, setMapReady] = useState(false);
  const [demoMode, setDemoMode] = useState<boolean | null>(null);

  useEffect(() => {
    if (mapRef.current || !mapContainer.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: [92.5, 26],
      zoom: 5.2,
    });

    mapRef.current = map;

    map.on("load", () => {
      setMapReady(true);
    });

    NER_CENTERS.forEach((c) => {
      const marker = new maplibregl.Marker({ color: "#3ba7ff" })
        .setLngLat([c.lon, c.lat])
        .setPopup(
          new maplibregl.Popup().setText(c.name)
        )
        .addTo(map);

      marker.getElement().addEventListener("click", () => {
        setSelected(c);
      });
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !infrastructure?.assets) return;

    // Remove old infrastructure markers
    infrastructureMarkersRef.current.forEach((marker) => marker.remove());
    infrastructureMarkersRef.current = [];

    const markerColors: Record<string, string> = {
      road: "#f59e0b",
      bridge: "#a855f7",
      settlement: "#ef4444",
      hospital: "#22c55e",
      school: "#06b6d4",
    };

    infrastructure.assets.forEach((asset: any) => {
      const color = markerColors[asset.type] || "#ffffff";

      const population =
        asset.estimated_population != null
          ? ` • Population: ${asset.estimated_population}`
          : "";

      const popup = new maplibregl.Popup({ offset: 25 }).setText(
        `${asset.name} • ${asset.type}${population}`
      );

      const marker = new maplibregl.Marker({ color })
        .setLngLat([asset.longitude, asset.latitude])
        .setPopup(popup)
        .addTo(mapRef.current!);

      infrastructureMarkersRef.current.push(marker);
    });
    mapRef.current.flyTo({
      center: [selected.lon, selected.lat],
      zoom: 10,
      essential: true,
    });

    return () => {
      infrastructureMarkersRef.current.forEach((marker) => marker.remove());
      infrastructureMarkersRef.current = [];
    };
  }, [infrastructure, mapReady]);

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setError(null);

    Promise.all([
      api.dataSourceStatus(),
      api.risk(selected.lat, selected.lon, selected.name),
      api.weather(selected.lat, selected.lon),
      api.alerts(selected.lat, selected.lon),
      api.infrastructure(selected.lat, selected.lon),
    ])
      .then(([sourceStatus, risk, weatherData, alertData, infrastructureData]) => {
        if (cancelled) return;

        setDemoMode(sourceStatus.demo_mode);
        setAssessment(risk as RiskAssessment);
        setWeather(weatherData);
        setAlerts(alertData);
        setInfrastructure(infrastructureData);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selected]);

  const action = assessment
    ? getAction(assessment.category)
    : null;

  const weatherData = weather?.data ?? weather;

  const temperature =
    weatherData?.current?.temperature_c ??
    weatherData?.temperature_c ??
    weatherData?.current_temperature_c;

  const humidity =
    weatherData?.current?.relative_humidity_pct ??
    weatherData?.humidity_pct ??
    weatherData?.current_humidity_pct;

  const rainfall24 =
    weatherData?.rainfall_24h_mm ??
    weatherData?.current?.rainfall_24h_mm;

  const rainfall72 =
    weatherData?.rainfall_72h_mm ??
    weatherData?.current?.rainfall_72h_mm;

  return (
    <>
      <header className="header">
        <div className="title">
          🌄 NER Landslide Intelligence — Mission Control
        </div>

        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          {demoMode !== null && (
            <Badge status={demoMode ? "demo" : "live"} />
          )}

          <span className="muted">
            {assessment
              ? `Last update: ${new Date(
                assessment.timestamp
              ).toLocaleTimeString()}`
              : "—"}
          </span>
        </div>
      </header>

      <div className="layout">
        <nav className="sidebar">
          <div
            className="muted"
            style={{ marginBottom: 8, paddingLeft: 10 }}
          >
            DISTRICTS
          </div>

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
          <div
            ref={mapContainer}
            style={{ width: "100%", height: "100%" }}
          />
        </div>

        <aside className="panel">
          {error && (
            <div className="card">
              ⚠️ {error}
            </div>
          )}

          {loading && !assessment && (
            <div className="card">
              Loading live assessment…
            </div>
          )}

          {assessment && (
            <>
              {/* RISK SUMMARY */}
              <div className="card">
                <div className="muted">{selected.name}</div>

                <div className="risk-score">
                  {assessment.risk_score.toFixed(0)}
                </div>

                <span
                  className={`category-pill cat-${assessment.category}`}
                >
                  {assessment.category.replace("_", " ")}
                </span>

                <div
                  style={{ marginTop: 10 }}
                  className="muted"
                >
                  Probability{" "}
                  {Math.round(
                    assessment.risk_probability * 100
                  )}
                  % · Confidence{" "}
                  {Math.round(assessment.confidence * 100)}
                  % · Uncertainty ±
                  {Math.round(assessment.uncertainty * 100)}%
                </div>

                {assessment.trend_explanation && (
                  <div
                    className="muted"
                    style={{ marginTop: 8 }}
                  >
                    {assessment.trend_explanation}
                  </div>
                )}
              </div>

              {/* LIVE WEATHER */}
              <div className="card">
                <div
                  style={{
                    marginBottom: 10,
                    fontWeight: 600,
                  }}
                >
                  🌧️ Live Weather
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 8,
                  }}
                >
                  <div>
                    <div className="muted">Temperature</div>
                    <strong>
                      {temperature != null
                        ? `${Number(temperature).toFixed(1)} °C`
                        : "—"}
                    </strong>
                  </div>

                  <div>
                    <div className="muted">Humidity</div>
                    <strong>
                      {humidity != null
                        ? `${Number(humidity).toFixed(0)}%`
                        : "—"}
                    </strong>
                  </div>

                  <div>
                    <div className="muted">Rainfall 24h</div>
                    <strong>
                      {rainfall24 != null
                        ? `${Number(rainfall24).toFixed(1)} mm`
                        : "—"}
                    </strong>
                  </div>

                  <div>
                    <div className="muted">Rainfall 72h</div>
                    <strong>
                      {rainfall72 != null
                        ? `${Number(rainfall72).toFixed(1)} mm`
                        : "—"}
                    </strong>
                  </div>
                </div>

                <div style={{ marginTop: 10 }}>
                  <Badge status="live" />
                  <span
                    className="muted"
                    style={{ marginLeft: 8 }}
                  >
                    Open-Meteo
                  </span>
                </div>
              </div>

              {/* ACTION RECOMMENDATION */}
              {action && (
                <div className="card">
                  <div
                    style={{
                      marginBottom: 8,
                      fontWeight: 600,
                    }}
                  >
                    🚨 Recommended Action
                  </div>

                  <div
                    style={{
                      fontWeight: 600,
                      marginBottom: 6,
                    }}
                  >
                    {action.title}
                  </div>

                  <div className="muted">
                    {action.text}
                  </div>
                </div>
              )}

              {/* IMPACTED INFRASTRUCTURE */}
              {infrastructure?.assets?.length > 0 && (
                <div className="card">
                  <div style={{ marginBottom: 10, fontWeight: 600 }}>
                    🛣️ Critical Infrastructure
                  </div>

                  {infrastructure.assets.map((asset: any) => (
                    <div
                      key={asset.id}
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginBottom: 8,
                        fontSize: 13,
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 600 }}>
                          {asset.name}
                        </div>
                        <div className="muted">
                          {asset.type}
                          {asset.estimated_population
                            ? ` · Population ${asset.estimated_population}`
                            : ""}
                        </div>
                      </div>

                      <span className="muted">NEARBY</span>
                    </div>
                  ))}

                  <div style={{ marginTop: 8 }}>
                    <Badge status={infrastructure.envelope?.status || "demo"} />
                    <span className="muted" style={{ marginLeft: 8 }}>
                      Infrastructure data
                    </span>
                  </div>
                </div>
              )}

              {/* ALERT STATUS */}
              <div className="card">
                <div style={{ marginBottom: 8, fontWeight: 600 }}>
                  🚨 Alert Status
                </div>

                {alerts?.alert ? (
                  <div>
                    <strong>{alerts.alert.title || "Active Warning"}</strong>
                    <div className="muted" style={{ marginTop: 5 }}>
                      {alerts.alert.message || "Warning generated by risk engine."}
                    </div>
                  </div>
                ) : (
                  <div className="muted">
                    No active alert. Current risk category:{" "}
                    <strong>{alerts?.assessment_category || assessment.category}</strong>
                  </div>
                )}
              </div>
              {/* RISK DRIVERS */}
              <div className="card">
                <div
                  style={{
                    marginBottom: 10,
                    fontWeight: 600,
                  }}
                >
                  Top Risk Drivers
                </div>

                {assessment.drivers
                  .slice(0, 6)
                  .map((d) => (
                    <div
                      className="driver-row"
                      key={d.factor}
                    >
                      <div style={{ width: 140 }}>
                        {d.factor}
                      </div>

                      <div className="driver-bar-bg">
                        <div
                          className="driver-bar"
                          style={{
                            width: `${Math.min(
                              100,
                              Math.abs(d.contribution) *
                              100 *
                              2
                            )}%`,
                          }}
                        />
                      </div>

                      <div className="muted">
                        {Math.round(
                          Math.abs(d.contribution) * 100
                        )}
                        %
                      </div>
                    </div>
                  ))}
              </div>

              {/* DATA FRESHNESS */}
              <div className="card">
                <div
                  style={{
                    marginBottom: 10,
                    fontWeight: 600,
                  }}
                >
                  Data Freshness
                </div>

                {assessment.data_freshness.map((f) => (
                  <div
                    key={f.layer}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontSize: 13,
                      marginBottom: 6,
                    }}
                  >
                    <span>{f.layer}</span>
                    <Badge status={f.status} />
                  </div>
                ))}

                <div
                  className="muted"
                  style={{ marginTop: 6 }}
                >
                  Model {assessment.model_version} · Features{" "}
                  {assessment.feature_version}
                </div>
              </div>
            </>
          )}
        </aside>
      </div>
    </>
  );
}