import re

with open('/home/leke/safestation/sensor_reader.py', 'r') as f:
    content = f.read()

old = """    if motion_detected:
        alerts.append("motion_detected")"""

new = """    # Motion is informational only — logged but doesn't trigger incident
    # PIR picks up heat from MQ-2 heater on shared breadboard
    # if motion_detected:
    #     alerts.append("motion_detected")"""

content = content.replace(old, new)

with open('/home/leke/safestation/sensor_reader.py', 'w') as f:
    f.write(content)

print("Fixed — motion logged but won't trigger alerts")
