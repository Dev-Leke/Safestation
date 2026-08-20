export default function SensorOverview({ telemetry, device }) {
  if (!telemetry) {
    return (
      <div className="card">
        <h2>Live Sensor Readings</h2>
        <p className="muted">Waiting for telemetry from the station...</p>
      </div>
    );
  }

  const online = device?.online ?? false;

  return (
    <div className="card">
      <div className="card-header">
        <h2>Live Sensor Readings</h2>
        <span className={`badge ${online ? "badge-online" : "badge-offline"}`}>
          {online ? "Station Online" : "Station Offline"}
        </span>
      </div>
      <p className="muted small">
        {telemetry.device_id} &middot; {telemetry.room}
      </p>
      <div className="stat-grid">
        <Stat
          label="Temperature"
          value={`${telemetry.temperature_c ?? "--"} °C`}
          warn={telemetry.temperature_c > 45}
        />
        <Stat label="Humidity" value={`${telemetry.humidity_pct ?? "--"} %`} />
        <Stat
          label="Gas Level"
          value={telemetry.gas_level ?? "--"}
          warn={telemetry.gas_level > 700}
        />
        <Stat
          label="Flame"
          value={telemetry.flame_detected ? "DETECTED" : "Clear"}
          warn={telemetry.flame_detected}
        />
        <Stat
          label="Motion"
          value={telemetry.motion_detected ? "Detected" : "None"}
        />
        <Stat
          label="Last Reading"
          value={
            telemetry.timestamp
              ? new Date(telemetry.timestamp).toLocaleTimeString()
              : "--"
          }
        />
      </div>
    </div>
  );
}

function Stat({ label, value, warn }) {
  return (
    <div className={`stat ${warn ? "stat-warn" : ""}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}
