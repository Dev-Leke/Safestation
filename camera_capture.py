"""
SafeStation AI — Camera capture
Takes a snapshot when an incident is detected.
"""

import os
import time
from datetime import datetime
from config import SNAPSHOT_DIR


def capture_snapshot():
    """
    Take a photo and save it with a timestamped filename.
    Returns the file path, or None if camera fails.
    """
    try:
        from picamera2 import Picamera2

        camera = Picamera2()
        camera.configure(camera.create_still_configuration())
        camera.start()
        time.sleep(1)  # Let the camera adjust to light

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"incident_{timestamp}.jpg"
        filepath = os.path.join(SNAPSHOT_DIR, filename)

        camera.capture_file(filepath)
        camera.stop()
        camera.close()

        print(f"  SNAPSHOT: {filepath}")
        return filepath

    except Exception as e:
        print(f"  CAMERA ERROR: {e}")
        return None


if __name__ == "__main__":
    path = capture_snapshot()
    if path:
        print(f"Saved to {path}")
    else:
        print("Camera not available")
