import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import SensorOverview from "./components/SensorOverview.jsx";
import IncidentList from "./components/IncidentList.jsx";
import IncidentDetail from "./components/IncidentDetail.jsx";

const POLL_MS = 4000;

export default function App() {
  const [telemetry, setTelemetry] = useState(null);
  const [device, setDevice] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [apiOnline, setApiOnline] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const [t, devices, inc] = await Promise.all([
        api.latestTelemetry(),
        api.devices(),
        api.incidents(),
      ]);
      setTelemetry(t);
      setDevice(devices.find((d) => d.device_id === (t?.device_id || "pi-station-01")) || null);
      setIncidents(inc);
      setApiOnline(true);
    } catch (e) {
      setApiOnline(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, POLL_MS);
    return () => clearInterval(id);
  }, [refresh]);

  const selected = incidents.find((i) => i.id === selectedId) || null;

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>SafeStation AI</h1>
          <p className="muted small">Cloud-native emergency detection &amp; response dashboard</p>
        </div>
        <span className={`badge ${apiOnline ? "badge-online" : "badge-offline"}`}>
          {apiOnline ? "API connected" : "API unreachable"}
        </span>
      </header>

      <SensorOverview telemetry={telemetry} device={device} />

      <div className="split">
        <IncidentList incidents={incidents} selectedId={selectedId} onSelect={setSelectedId} />
        <IncidentDetail incident={selected} onChanged={refresh} />
      </div>

      <footer className="footer muted small">
        Educational emergency-monitoring 
        
      </footer>
    </div>
  );
}