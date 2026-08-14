const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };

export default function IncidentList({ incidents, selectedId, onSelect }) {
  const sorted = [...incidents].sort((a, b) => {
    const sevDiff = (SEVERITY_ORDER[a.severity] ?? 9) - (SEVERITY_ORDER[b.severity] ?? 9);
    if (sevDiff !== 0) return sevDiff;
    return new Date(b.timestamp) - new Date(a.timestamp);
  });

  return (
    <div className="card">
      <h2>Incidents</h2>
      {sorted.length === 0 && <p className="muted">No incidents reported yet.</p>}
      <ul className="incident-list">
        {sorted.map((inc) => (
          <li
            key={inc.id}
            className={`incident-row severity-${inc.severity} ${inc.id === selectedId ? "selected" : ""}`}
            onClick={() => onSelect(inc.id)}
          >
            <div className="incident-row-top">
              <span className={`pill pill-${inc.severity}`}>{inc.severity}</span>
              <span className="incident-category">{inc.category}</span>
              <span className={`review-tag review-${inc.review_status}`}>{inc.review_status}</span>
            </div>
            <div className="incident-row-bottom">
              <span>{inc.room}</span>
              <span className="muted">{new Date(inc.timestamp + "Z").toLocaleTimeString()}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
