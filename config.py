"""
SafeStation AI — Edge configuration
All pin assignments, thresholds, and settings in one place.
"""

# ── Device identity ──────────────────────────────────────────
DEVICE_ID = "safestation-001"
BUILDING = "SAIT Lab"
ROOM = "Room 312"

# ── GPIO pins (BCM numbering) ────────────────────────────────
DHT11_PIN = 4
MQ2_DIGITAL_PIN = 17
FLAME_DIGITAL_PIN = 27
PIR_PIN = 22
BUZZER_PIN = 18

# ── Sensor thresholds (deterministic rules, not AI) ──────────
THRESHOLDS = {
    "temperature_high_c": 45.0,
    "temperature_low_c": 5.0,
    "humidity_high_pct": 85.0,
    "humidity_low_pct": 15.0,
}

# ── Timing ───────────────────────────────────────────────────
SENSOR_READ_INTERVAL_SEC = 5
TELEMETRY_UPLOAD_INTERVAL_SEC = 30
ALERT_COOLDOWN_SEC = 60

# ── PIR noise filter ────────────────────────────────────────
PIR_CONSECUTIVE_READINGS = 2  # Need 3 in a row to confirm motion

# ── Azure IoT Hub (loaded from .env at runtime) ─────────────
IOT_HUB_CONNECTION_STRING = ""

# ── Camera ───────────────────────────────────────────────────
SNAPSHOT_DIR = "/home/leke/safestation/snapshots"
