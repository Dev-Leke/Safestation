"""
SafeStation AI — Blob Storage uploader
Uploads camera snapshots to Azure Blob Storage.
"""

import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

blob_client = None
container_client = None


def connect_blob():
    """Connect to Azure Blob Storage."""
    global blob_client, container_client
    try:
        conn_str = os.getenv("BLOB_CONNECTION_STRING")
        container_name = os.getenv("BLOB_CONTAINER", "snapshots")
        blob_client = BlobServiceClient.from_connection_string(conn_str)
        container_client = blob_client.get_container_client(container_name)
        print("Connected to Blob Storage")
        return True
    except Exception as e:
        print(f"Blob Storage connection failed: {e}")
        return False


def upload_snapshot(filepath):
    """Upload a snapshot and return its public URL."""
    global container_client
    if container_client is None or filepath is None:
        return None
    try:
        filename = os.path.basename(filepath)
        blob = container_client.get_blob_client(filename)
        with open(filepath, "rb") as data:
            blob.upload_blob(data, overwrite=True)
        url = f"https://{blob_client.account_name}.blob.core.windows.net/{os.getenv('BLOB_CONTAINER', 'snapshots')}/{filename}"
        print(f"  >> Snapshot uploaded: {filename}")
        return url
    except Exception as e:
        print(f"  >> Snapshot upload failed: {e}")
        return None


if __name__ == "__main__":
    if connect_blob():
        # Test with an existing snapshot
        import glob
        snapshots = glob.glob("/home/leke/safestation/snapshots/*.jpg")
        if snapshots:
            url = upload_snapshot(snapshots[0])
            print(f"URL: {url}")
        else:
            print("No snapshots to test with")
