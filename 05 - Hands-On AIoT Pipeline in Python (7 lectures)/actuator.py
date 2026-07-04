import random
import time
import json

def generate_sensor_data():
    data = {
        "temperature": round(random.uniform(20, 35), 2),
        "humidity": round(random.uniform(40, 70), 2),
        "device_id": "sensor_001",
        "timestamp": time.time()
    }
    return data


def actuator_control(data):
    print("temperature : ", data)
    if data["temperature"] > 30:
        print("🌀 Fan ON")
    else:
        print("❌ Fan OFF")

# Test
actuator_control(generate_sensor_data())