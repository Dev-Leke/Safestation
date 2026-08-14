"""
SafeStation AI — Incident Triage Agent
Evaluates sensor events and produces structured severity assessments.
Uses Azure OpenAI to reason about sensor combinations.
"""

import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are the SafeStation AI Incident Triage Agent. You evaluate sensor events 
from an indoor emergency monitoring station and produce structured incident assessments.

RULES:
- Use ONLY the sensor data provided. Do not invent causes, occupant conditions, or details.
- Distinguish between a real incident and a possible sensor fault.
- If readings conflict or data is missing, lower your confidence.
- Gas + flame + high temperature together = highest severity.
- A single sensor trigger with no corroboration = lower confidence.
- Motion alone is informational, not an emergency.
- Require human review when severity is high/critical or confidence is below 0.7.
- Never declare a building safe. Never diagnose medical conditions.

RESPOND WITH ONLY valid JSON matching this exact schema, no other text:
{
    "category": "fire | gas | motion | temperature | combined | sensor_fault",
    "severity": "low | medium | high | critical",
    "confidence": 0.00,
    "evidence": [],
    "recommended_action": "",
    "requires_human_review": true,
    "alert_summary": ""
}"""


client = None


def connect_openai():
    """Initialize the Azure OpenAI client."""
    global client
    try:
        client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-12-01-preview"
        )
        print("Connected to Azure OpenAI")
        return True
    except Exception as e:
        print(f"Azure OpenAI connection failed: {e}")
        return False


def triage_incident(event):
    """
    Send a sensor event to the triage agent and get a structured assessment.
    Returns a dictionary with category, severity, confidence, etc.
    """
    global client
    if client is None:
        return None

    # Build the event summary for the agent
    event_description = f"""Evaluate this sensor event from device {event['device_id']} 
at {event['building']}, {event['room']}:

Timestamp: {event['timestamp']}
Temperature: {event['temperature_c']}°C
Humidity: {event['humidity_pct']}%
Gas detected: {event['gas_detected']}
Flame detected: {event['flame_detected']}
Motion detected: {event['motion_detected']}
DHT sensor status: {event['dht_status']}
Active alerts: {', '.join(event['alerts']) if event['alerts'] else 'none'}"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": event_description}
            ],
            temperature=0.1,
            max_completion_tokens=500
        )

        result_text = response.choices[0].message.content.strip()

        # Clean markdown fencing if present
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1]
            result_text = result_text.rsplit("```", 1)[0]

        assessment = json.loads(result_text)
        print(f"  >> Triage: {assessment['severity']} severity, "
              f"confidence {assessment['confidence']}, "
              f"category: {assessment['category']}")
        return assessment

    except Exception as e:
        print(f"  >> Triage agent error: {e}")
        return None


if __name__ == "__main__":
    if connect_openai():
        # Test with a simulated flame incident
        test_event = {
            "device_id": "safestation-001",
            "building": "SAIT Lab",
            "room": "Room 312",
            "timestamp": "2026-08-14T01:00:00+00:00",
            "temperature_c": 24.5,
            "humidity_pct": 44,
            "gas_detected": False,
            "flame_detected": True,
            "motion_detected": False,
            "dht_status": "ok",
            "alerts": ["flame_detected"],
            "is_incident": True
        }
        print("\nTest 1: Flame only")
        result = triage_incident(test_event)
        if result:
            print(json.dumps(result, indent=2))

        # Test with combined gas + flame
        test_event2 = {
            "device_id": "safestation-001",
            "building": "SAIT Lab",
            "room": "Room 312",
            "timestamp": "2026-08-14T01:01:00+00:00",
            "temperature_c": 48.0,
            "humidity_pct": 30,
            "gas_detected": True,
            "flame_detected": True,
            "motion_detected": True,
            "dht_status": "ok",
            "alerts": ["gas_detected", "flame_detected", "temperature_high"],
            "is_incident": True
        }
        print("\nTest 2: Gas + Flame + High Temp")
        result2 = triage_incident(test_event2)
        if result2:
            print(json.dumps(result2, indent=2))
