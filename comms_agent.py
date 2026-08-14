"""
SafeStation AI — Emergency Communication Agent
Sends email alerts via Azure Communication Services.
"""

import os
import json
from azure.communication.email import EmailClient
from dotenv import load_dotenv

load_dotenv()

email_client = None


def connect_comms():
    """Initialize Azure email client."""
    global email_client
    try:
        conn_str = os.getenv("ACS_CONNECTION_STRING")
        email_client = EmailClient.from_connection_string(conn_str)
        print("Communication agent ready")
        return True
    except Exception as e:
        print(f"Communication agent failed: {e}")
        return False


def send_alert_email(event):
    """Send an email alert for an incident."""
    global email_client
    if email_client is None:
        return False

    try:
        triage = event.get("triage", {})
        category = triage.get("category", "unknown")
        severity = triage.get("severity", "unknown")
        confidence = triage.get("confidence", 0)
        summary = triage.get("alert_summary", "No summary available")
        action = triage.get("recommended_action", "Check dashboard")
        evidence = triage.get("evidence", [])

        subject = f"SafeStation Alert: {severity.upper()} - {category} at {event.get('room', 'Unknown')}"

        body = f"""SafeStation AI — Incident Alert
========================================

Location: {event.get('building', 'Unknown')}, {event.get('room', 'Unknown')}
Time: {event.get('timestamp', 'Unknown')}
Category: {category}
Severity: {severity.upper()}
Confidence: {confidence}

Summary:
{summary}

Sensor Readings:
- Temperature: {event.get('temperature_c', 'N/A')}°C
- Humidity: {event.get('humidity_pct', 'N/A')}%
- Gas detected: {event.get('gas_detected', False)}
- Flame detected: {event.get('flame_detected', False)}
- Motion detected: {event.get('motion_detected', False)}

Evidence:
{chr(10).join('- ' + e for e in evidence)}

Recommended Action:
{action}

Human Review Required: {triage.get('requires_human_review', True)}

========================================
This is an automated alert from SafeStation AI.
This system is an educational prototype, not a certified life-safety system.
"""

        message = {
            "senderAddress": os.getenv("ACS_SENDER"),
            "recipients": {
                "to": [{"address": os.getenv("ALERT_EMAIL")}]
            },
            "content": {
                "subject": subject,
                "plainText": body
            }
        }

        poller = email_client.begin_send(message)
        result = poller.result()
        print(f"  >> Email sent: {result['id'][:20]}...")
        return True
    except Exception as e:
        print(f"  >> Email failed: {e}")
        return False


if __name__ == "__main__":
    if connect_comms():
        test_event = {
            "device_id": "safestation-001",
            "building": "SAIT Lab",
            "room": "Room 312",
            "timestamp": "2026-08-14T02:00:00+00:00",
            "temperature_c": 24.5,
            "humidity_pct": 44,
            "gas_detected": False,
            "flame_detected": True,
            "motion_detected": False,
            "alerts": ["flame_detected"],
            "is_incident": True,
            "triage": {
                "category": "fire",
                "severity": "medium",
                "confidence": 0.65,
                "evidence": ["Flame sensor triggered", "Normal temperature", "No gas detected"],
                "recommended_action": "Send personnel to verify flame in Room 312",
                "requires_human_review": True,
                "alert_summary": "Flame detected in Room 312 with no corroborating signals"
            }
        }
        print("\nSending test email...")
        send_alert_email(test_event)
