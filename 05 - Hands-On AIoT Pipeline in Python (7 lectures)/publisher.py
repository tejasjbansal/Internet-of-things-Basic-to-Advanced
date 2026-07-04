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


import paho.mqtt.client as mqtt
import time, json

broker = "localhost"
port = 1883
topic = "iot/sensor/data"

client = mqtt.Client()
client.connect(broker, port)

print("Publishing sensor data... Press Ctrl+C to stop.")
try:
    while True:
        data = generate_sensor_data()
        client.publish(topic, json.dumps(data))
        print("Published:", data)
        time.sleep(2)
except KeyboardInterrupt:
    print("Stopped publisher.")
    client.disconnect()