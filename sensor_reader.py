"""
SafeStation AI — Sensor reader
Reads all sensors, checks thresholds, returns a structured event.
"""

import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
from datetime import datetime, timezone
from config import (
    DHT11_PIN, MQ2_DIGITAL_PIN, FLAME_DIGITAL_PIN, PIR_PIN,
    DEVICE_ID, BUILDING, ROOM, THRESHOLDS
)

# Initialize DHT11 sensor once (reused across readings)
dht_sensor = adafruit_dht.DHT11(board.D4)


def setup_gpio():
    """Configure all GPIO pins. Called once at startup."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MQ2_DIGITAL_PIN, GPIO.IN)
    GPIO.setup(FLAME_DIGITAL_PIN, GPIO.IN)
    GPIO.setup(PIR_PIN, GPIO.IN)


def read_pir_filtered():
    """
    Sample PIR 10 times over 1 second.
    Real motion triggers 7+ out of 10 reads.
    Noise triggers 1-3 randomly.
    """
    highs = 0
    for _ in range(10):
        if GPIO.input(PIR_PIN) == GPIO.HIGH:
            highs += 1
        time.sleep(0.1)
    return highs >= 7


def read_sensors():
    """
    Read every sensor and return a dictionary with all values.
    """

    # ── DHT11: temperature and humidity ──────────────────────
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        dht_status = "ok"
    except RuntimeError:
        temperature = None
        humidity = None
        dht_status = "read_error"

    # ── MQ-2: gas detection (active low) ────────────────────
    gas_detected = GPIO.input(MQ2_DIGITAL_PIN) == GPIO.LOW

    # ── Flame sensor: fire detection (active low) ───────────
    flame_detected = GPIO.input(FLAME_DIGITAL_PIN) == GPIO.LOW

    # ── PIR: motion detection with noise filter ─────────────
    motion_detected = read_pir_filtered()

    # ── Check thresholds ────────────────────────────────────
    alerts = []

    if gas_detected:
        alerts.append("gas_detected")

    if flame_detected:
        alerts.append("flame_detected")

    # Motion is informational only — logged but doesn't trigger incident
    # PIR picks up heat from MQ-2 heater on shared breadboard
    # if motion_detected:
    #     alerts.append("motion_detected")

    if temperature is not None:
        if temperature >= THRESHOLDS["temperature_high_c"]:
            alerts.append("temperature_high")
        elif temperature <= THRESHOLDS["temperature_low_c"]:
            alerts.append("temperature_low")

    if humidity is not None:
        if humidity >= THRESHOLDS["humidity_high_pct"]:
            alerts.append("humidity_high")
        elif humidity <= THRESHOLDS["humidity_low_pct"]:
            alerts.append("humidity_low")

    # ── Determine if this is an incident ────────────────────
    is_incident = len(alerts) > 0

    # ── Build the event dictionary ──────────────────────────
    event = {
        "device_id": DEVICE_ID,
        "building": BUILDING,
        "room": ROOM,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": temperature,
        "humidity_pct": humidity,
        "gas_detected": gas_detected,
        "flame_detected": flame_detected,
        "motion_detected": motion_detected,
        "dht_status": dht_status,
        "alerts": alerts,
        "is_incident": is_incident
    }

    return event


if __name__ == "__main__":
    """Quick test — read sensors 5 times."""
    setup_gpio()
    try:
        for i in range(5):
            event = read_sensors()
            print(f"\n── Reading {i+1} ──")
            for key, value in event.items():
                print(f"  {key}: {value}")
            time.sleep(3)
    finally:
        GPIO.cleanup()
