"""
SafeStation AI — Flask API
Bridges Cosmos DB data to the React dashboard.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
CORS(app)

# Cosmos DB connection
endpoint = os.getenv("COSMOS_ENDPOINT")
key = os.getenv("COSMOS_KEY")
client = CosmosClient(endpoint, key) if endpoint and key else None
database = client.get_database_client("safestation") if client else None
container = database.get_container_client("incidents") if database else None


def flatten_incident(doc):
    """Flatten triage data to top level for the dashboard."""
    triage = doc.get("triage", {})
    return {
        "id": doc.get("id"),
        "event_id": doc.get("id", ""),
        "device_id": doc.get("device_id", ""),
        "building": doc.get("building", ""),
        "room": doc.get("room", ""),
        "timestamp": doc.get("timestamp", ""),
        "temperature_c": doc.get("temperature_c"),
        "humidity_pct": doc.get("humidity_pct"),
        "gas_detected": doc.get("gas_detected", False),
        "gas_level": 800 if doc.get("gas_detected") else 50,
        "flame_detected": doc.get("flame_detected", False),
        "motion_detected": doc.get("motion_detected", False),
        "category": triage.get("category", "unknown"),
        "severity": triage.get("severity", "low"),
        "confidence": triage.get("confidence", 0),
        "evidence": triage.get("evidence", []),
        "recommended_action": triage.get("recommended_action", ""),
        "alert_summary": triage.get("alert_summary", ""),
        "requires_human_review": triage.get("requires_human_review", True),
        "review_status": doc.get("review_status", "pending"),
        "reviewed_by": doc.get("reviewed_by", ""),
        "review_notes": doc.get("review_notes", ""),
        "notification_status": doc.get("notification_status", "not_sent"),
        "notification_payload": doc.get("notification_payload"),
        "snapshot_ref": doc.get("snapshot_path", ""),
        "alerts": doc.get("alerts", []),
        "event_type": doc.get("event_type", "routine"),
    }


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "SafeStation AI API"})


@app.route("/api/devices")
def get_devices():
    """Return known devices with online status."""
    devices = [{
        "device_id": "safestation-001",
        "building": "SAIT Lab",
        "room": "Room 312",
        "online": True
    }]
    return jsonify(devices)


@app.route("/api/telemetry/latest")
def get_latest_telemetry():
    """Get the most recent telemetry reading."""
    if not container:
        return jsonify({"error": "Database not connected"}), 500
    try:
        query = "SELECT TOP 1 * FROM c ORDER BY c.timestamp DESC"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        if items:
            doc = items[0]
            return jsonify({
                "device_id": doc.get("device_id", "safestation-001"),
                "building": doc.get("building", ""),
                "room": doc.get("room", ""),
                "timestamp": doc.get("timestamp", ""),
                "temperature_c": doc.get("temperature_c"),
                "humidity_pct": doc.get("humidity_pct"),
                "gas_detected": doc.get("gas_detected", False),
                "gas_level": 800 if doc.get("gas_detected") else 50,
                "flame_detected": doc.get("flame_detected", False),
                "motion_detected": doc.get("motion_detected", False),
            })
        return jsonify({}), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/telemetry/history")
def get_telemetry_history():
    """Get recent telemetry readings."""
    if not container:
        return jsonify({"error": "Database not connected"}), 500
    try:
        limit = request.args.get("limit", 30, type=int)
        query = f"SELECT TOP {limit} * FROM c ORDER BY c.timestamp DESC"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/incidents")
def get_incidents():
    """Get all incidents with flattened triage data."""
    if not container:
        return jsonify({"error": "Database not connected"}), 500
    try:
        query = "SELECT * FROM c WHERE c.event_type = 'incident' ORDER BY c.timestamp DESC"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        return jsonify([flatten_incident(doc) for doc in items])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/incidents/<incident_id>")
def get_incident(incident_id):
    """Get a single incident by ID."""
    if not container:
        return jsonify({"error": "Database not connected"}), 500
    try:
        query = f"SELECT * FROM c WHERE c.id = '{incident_id}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        if items:
            return jsonify(flatten_incident(items[0]))
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/incidents/<incident_id>/review", methods=["POST", "PATCH"])
def review_incident(incident_id):
    """Human review — approve or reject an incident."""
    if not container:
        return jsonify({"error": "Database not connected"}), 500
    try:
        data = request.json
        query = f"SELECT * FROM c WHERE c.id = '{incident_id}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        if not items:
            return jsonify({"error": "Not found"}), 404

        item = items[0]
        item["review_status"] = data.get("decision", data.get("status", "reviewed"))
        item["review_notes"] = data.get("notes", "")
        item["reviewed_by"] = data.get("reviewer", "unknown")
        container.upsert_item(item)
        return jsonify(flatten_incident(item))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/incidents/<incident_id>/notify", methods=["POST"])
def notify_incident(incident_id):
    """Send notification for an approved incident."""
    if not container:
        return jsonify({"error": "Database not connected"}), 500
    try:
        query = f"SELECT * FROM c WHERE c.id = '{incident_id}'"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        if not items:
            return jsonify({"error": "Not found"}), 404

        item = items[0]
        # Import and send email notification
        try:
            from comms_agent import connect_comms, send_alert_email
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            connect_comms()
            send_alert_email(item)
            item["notification_status"] = "sent"
            item["notification_payload"] = {
                "sms_text": f"SafeStation Alert: {item.get('triage', {}).get('category', 'unknown')} at {item.get('room', '')}",
                "email_subject": f"SafeStation Alert: {item.get('triage', {}).get('severity', 'unknown')} incident",
                "email_body": item.get('triage', {}).get('alert_summary', '')
            }
        except Exception as notify_err:
            item["notification_status"] = "failed"
            item["notification_payload"] = {"error": str(notify_err)}

        container.upsert_item(item)
        return jsonify(flatten_incident(item))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
