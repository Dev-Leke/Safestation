"""
SafeStation AI — Main entry point
Reads sensors, triggers alerts, sends telemetry to Azure IoT Hub,
stores events in Cosmos DB, and triages incidents with AI.
"""

import RPi.GPIO as GPIO
import time
import json
import os
from dotenv import load_dotenv
from azure.iot.device import IoTHubDeviceClient, Message
from config import SENSOR_READ_INTERVAL_SEC, TELEMETRY_UPLOAD_INTERVAL_SEC
from sensor_reader import setup_gpio, read_sensors
from alert_manager import setup_buzzer, trigger_alert, silence_buzzer
from camera_capture import capture_snapshot
from cosmos_client import connect_cosmos, store_event
from triage_agent import connect_openai, triage_incident

load_dotenv()


def connect_iot_hub():
    conn_str = os.getenv("IOT_HUB_CONNECTION_STRING")
    if not conn_str:
        return None
    try:
        client = IoTHubDeviceClient.create_from_connection_string(conn_str)
        client.connect()
        print("Connected to Azure IoT Hub")
        return client
    except Exception as e:
        print(f"IoT Hub connection failed: {e}")
        return None


def send_telemetry(client, event):
    try:
        message = Message(json.dumps(event, default=str))
        message.content_type = "application/json"
        message.content_encoding = "utf-8"
        if event.get("is_incident"):
            message.custom_properties["alert_type"] = "incident"
        else:
            message.custom_properties["alert_type"] = "routine"
        client.send_message(message)
        print(f"  >> Sent to IoT Hub ({len(message.data)} bytes)")
    except Exception as e:
        print(f"  >> IoT Hub send failed: {e}")


def main():
    print("=" * 50)
    print("  SafeStation AI — Starting up")
    print("=" * 50)

    GPIO.setmode(GPIO.BCM)
    setup_gpio()
    setup_buzzer()

    iot_client = connect_iot_hub()
    cosmos_connected = connect_cosmos()
    ai_connected = connect_openai()

    print("\nAll systems initialized. Monitoring started.")
    print("Press Ctrl+C to stop.\n")

    last_upload_time = time.time()
    reading_count = 0

    try:
        while True:
            event = read_sensors()
            reading_count += 1

            if event["is_incident"]:
                trigger_alert(event["alerts"])

                # Camera snapshot
                snapshot_path = capture_snapshot()
                event["snapshot_path"] = snapshot_path if snapshot_path else "snapshot_unavailable"

                # AI triage
                if ai_connected:
                    assessment = triage_incident(event)
                    if assessment:
                        event["triage"] = assessment

                print(f"\n*** INCIDENT #{reading_count} ***")
                print(f"  Alerts: {', '.join(event['alerts'])}")
                print(f"  Temp: {event['temperature_c']}C | Humidity: {event['humidity_pct']}%")
                print(f"  Gas: {event['gas_detected']} | Flame: {event['flame_detected']}")
                if "triage" in event:
                    t = event["triage"]
                    print(f"  AI Triage: {t['severity']} | Confidence: {t['confidence']}")
                    print(f"  Summary: {t['alert_summary']}")

                if iot_client:
                    send_telemetry(iot_client, event)
                if cosmos_connected:
                    store_event(event)
            else:
                silence_buzzer()
                if reading_count % 6 == 0:
                    print(f"  [{reading_count}] Normal — {event['temperature_c']}C, {event['humidity_pct']}% humidity")

            # Routine telemetry every 30 seconds
            now = time.time()
            if now - last_upload_time >= TELEMETRY_UPLOAD_INTERVAL_SEC:
                if iot_client:
                    send_telemetry(iot_client, event)
                if cosmos_connected:
                    store_event(event)
                last_upload_time = now

            time.sleep(SENSOR_READ_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\n\nShutting down SafeStation AI...")
    finally:
        silence_buzzer()
        GPIO.cleanup()
        if iot_client:
            iot_client.disconnect()
            print("Disconnected from Azure IoT Hub")
        print("GPIO cleaned up. Goodbye.")

if __name__ == "__main__":
    main()
