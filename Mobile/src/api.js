const API_BASE = "http://172.20.10.11:5050/api";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  health: () => request("/health"),
  latestTelemetry: (deviceId = "pi-station-01") =>
    request(`/telemetry/latest?device_id=${encodeURIComponent(deviceId)}`),
  devices: () => request("/devices"),
  incidents: (status) => request(`/incidents${status ? `?status=${status}` : ""}`),
  incident: (id) => request(`/incidents/${id}`),
  reviewIncident: (id, decision, reviewer) =>
    request(`/incidents/${id}/review`, {
      method: "PATCH",
      body: JSON.stringify({ decision, reviewer }),
    }),
  notifyIncident: (id) => request(`/incidents/${id}/notify`, { method: "POST" }),
};