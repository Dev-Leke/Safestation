const API_BASE = import.meta.env.VITE_API_BASE || "/api";

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
  latestTelemetry: (deviceId = "safestation-001") =>
    request(`/telemetry/latest?device_id=${encodeURIComponent(deviceId)}`),
  telemetryHistory: (deviceId = "safestation-001", limit = 30) =>
    request(`/telemetry/history?device_id=${encodeURIComponent(deviceId)}&limit=${limit}`),
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