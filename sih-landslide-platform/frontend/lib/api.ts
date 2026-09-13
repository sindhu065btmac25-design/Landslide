const BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Request failed: ${path} (${res.status})`);
  return res.json();
}

export const api = {
  risk: (lat: number, lon: number, name?: string) =>
    getJson(`/api/v1/risk/location/${lat}/${lon}${name ? `?name=${encodeURIComponent(name)}` : ""}`),
  riskGrid: () => getJson(`/api/v1/risk/grid`),
  weather: (lat: number, lon: number) => getJson(`/api/v1/weather/current?lat=${lat}&lon=${lon}`),
  satellite: (lat: number, lon: number) => getJson(`/api/v1/satellite/latest?lat=${lat}&lon=${lon}`),
  infrastructure: (lat: number, lon: number) => getJson(`/api/v1/infrastructure?lat=${lat}&lon=${lon}`),
  alerts: (lat: number, lon: number) => getJson(`/api/v1/alerts?lat=${lat}&lon=${lon}`),
  dataSourceStatus: () => getJson(`/data-sources/status`),
};
