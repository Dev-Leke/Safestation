"""
SafeStation AI — Cosmos DB client
Stores telemetry and incidents in Azure Cosmos DB.
"""

import os
import uuid
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv

load_dotenv()

cosmos_client = None
container = None


def connect_cosmos():
    """Connect to Cosmos DB and get the incidents container."""
    global cosmos_client, container
    try:
        endpoint = os.getenv("COSMOS_ENDPOINT")
        key = os.getenv("COSMOS_KEY")
        database_name = os.getenv("COSMOS_DATABASE")
        container_name = os.getenv("COSMOS_CONTAINER")

        cosmos_client = CosmosClient(endpoint, key)
        database = cosmos_client.get_database_client(database_name)
        container = database.get_container_client(container_name)
        print("Connected to Cosmos DB")
        return True
    except Exception as e:
        print(f"Cosmos DB connection failed: {e}")
        return False


def store_event(event):
    """
    Store a sensor event in Cosmos DB.
    Adds a unique id required by Cosmos DB.
    """
    global container
    if container is None:
        return False
    try:
        # Cosmos DB requires a unique 'id' field
        doc = event.copy()
        doc["id"] = str(uuid.uuid4())

        # Add event type for easier querying
        if event["is_incident"]:
            doc["event_type"] = "incident"
        else:
            doc["event_type"] = "routine"

        container.create_item(body=doc)
        print(f"  >> Stored in Cosmos DB (id: {doc['id'][:8]}...)")
        return True
    except Exception as e:
        print(f"  >> Cosmos DB write failed: {e}")
        return False


if __name__ == "__main__":
    if connect_cosmos():
        test_event = {
            "device_id": "safestation-001",
            "building": "SAIT Lab",
            "room": "Room 312",
            "timestamp": "2026-08-14T00:00:00+00:00",
            "temperature_c": 24.5,
            "humidity_pct": 44,
            "gas_detected": False,
            "flame_detected": True,
            "motion_detected": False,
            "dht_status": "ok",
            "alerts": ["flame_detected"],
            "is_incident": True
        }
        store_event(test_event)
        print("Test event stored successfully")
    else:
        print("Could not connect to Cosmos DB")
