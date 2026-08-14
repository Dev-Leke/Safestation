"""
SafeStation AI — Flask API
Serves incident and telemetry data to the React dashboard.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from azure.cosmos import CosmosClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Cosmos DB connection
endpoint = os.getenv("COSMOS_ENDPOINT")
key = os.getenv("COSMOS_KEY")
client = CosmosClient(endpoint, key) if endpoint and key else None
database = client.get_database_client("safestation") if client else None
container = database.get_container_client("incidents") if database else None


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "SafeStation AI API"})


@app.route("/api/incidents")
def get_incidents():
    """Get all incidents, newest first."""
    if not container:
        return jsonify({"error": "Database not connected"}), 500
    try:
        query = "SELECT * FROM c WHERE c.event_type = 'incident' ORDER BY c.timestamp DESC"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        return jsonify(items)
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
            return jsonify(items[0])
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/telemetry")
def get_telemetry():
    """Get recent telemetry readings."""
    if not container:
        return jsonify({"error": "Database not connected"}), 500
    try:
        query = "SELECT * FROM c ORDER BY c.timestamp DESC OFFSET 0 LIMIT 50"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        return jsonify(items)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/incidents/<incident_id>/review", methods=["POST"])
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
        item["review_status"] = data.get("status", "reviewed")
        item["review_notes"] = data.get("notes", "")
        item["reviewed_by"] = data.get("reviewer", "unknown")
        container.upsert_item(item)
        return jsonify({"message": "Review saved", "incident": item})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
