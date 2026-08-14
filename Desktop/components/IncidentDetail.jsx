import { useState } from "react";
import { api } from "../api.js";

export default function IncidentDetail({ incident, onChanged }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  if (!incident) {
    return (
      <div className="card">
        <h2>Incident detail</h2>
        <p className="muted">Select an incident from the list to review it.</p>
      </div>
    );
  }

  const act = async (fn) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      await onChanged();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Incident {incident.event_id.slice(0, 8)}</h2>
        <span className={`pill pill-${incident.severity}`}>{incident.severity}</span>
      </div>

      <p className="muted small">
        {incident.room} &middot; {incident.device_id} &middot;{" "}
        {new Date(incident.timestamp + "Z").toLocaleString()}
      </p>

      <p className="alert-summary">{incident.alert_summary}</p>

      <div className="detail-grid">
        <div>
          <div className="stat-label">Category</div>
          <div>{incident.category}</div>
        </div>
        <div>
          <div className="stat-label">Confidence</div>
          <div>{(incident.confidence * 100).toFixed(0)}%</div>
        </div>
        <div>
          <div className="stat-label">Review Status</div>
          <div className={`review-tag review-${incident.review_status}`}>{incident.review_status}</div>
        </div>
        <div>
          <div className="stat-label">Notification</div>
          <div>{incident.notification_status}</div>
        </div>
      </div>

      <h3>Evidence</h3>
      {incident.evidence.length === 0 ? (
        <p className="muted">No supporting evidence recorded.</p>
      ) : (
        <ul className="evidence-list">
          {incident.evidence.map((e, i) => (
            <li key={i}>{e}</li>
          ))}
        </ul>
      )}

      <h3>Recommended Action</h3>
      <p>{incident.recommended_action || "—"}</p>

      {incident.snapshot_ref && (
        <p className="muted small">Camera snapshot: {incident.snapshot_ref}</p>
      )}

      <div className="actions">
        {incident.review_status === "pending" && (
          <>
            <button
              disabled={busy}
              className="btn btn-approve"
              onClick={() => act(() => api.reviewIncident(incident.id, "approved", "abimbola"))}
            >
              Approve
            </button>
            <button
              disabled={busy}
              className="btn btn-reject"
              onClick={() => act(() => api.reviewIncident(incident.id, "rejected", "abimbola"))}
            >
              Reject
            </button>
          </>
        )}
        {incident.review_status === "approved" && incident.notification_status !== "sent" && (
          <button disabled={busy} className="btn btn-notify" onClick={() => act(() => api.notifyIncident(incident.id))}>
            Send notification
          </button>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {incident.notification_payload && (
        <div className="notification-preview">
          <h3>Sent Notification</h3>
          <p>
            <strong>SMS:</strong> {incident.notification_payload.sms_text}
          </p>
          <p>
            <strong>Email subject:</strong> {incident.notification_payload.email_subject}
          </p>
          <pre>{incident.notification_payload.email_body}</pre>
        </div>
      )}
    </div>
  );
}