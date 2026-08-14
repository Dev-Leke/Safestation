"""
SafeStation AI — Alert manager
Controls the buzzer for local alerts with cooldown logic.
"""

import RPi.GPIO as GPIO
import time
from config import BUZZER_PIN, ALERT_COOLDOWN_SEC

# Track when the last alert fired
last_alert_time = 0


def setup_buzzer():
    """Configure buzzer pin. Called once at startup."""
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    GPIO.output(BUZZER_PIN, GPIO.LOW)


def trigger_alert(alerts):
    """
    Sound the buzzer if there are active alerts
    and cooldown period has passed.
    Returns True if buzzer was activated.
    """
    global last_alert_time

    if not alerts:
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        return False

    now = time.time()
    if now - last_alert_time < ALERT_COOLDOWN_SEC:
        return False

    # Buzzer pattern: 3 short beeps for urgency
    for i in range(3):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.2)

    last_alert_time = now
    print(f"  BUZZER ALERT: {', '.join(alerts)}")
    return True


def silence_buzzer():
    """Turn off the buzzer."""
    GPIO.output(BUZZER_PIN, GPIO.LOW)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    setup_buzzer()
    try:
        print("Testing buzzer alert...")
        trigger_alert(["gas_detected", "flame_detected"])
        time.sleep(2)
        print("Testing silence...")
        silence_buzzer()
        print("Done")
    finally:
        GPIO.cleanup()
