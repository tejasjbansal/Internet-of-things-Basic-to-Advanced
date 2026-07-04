import paho.mqtt.client as mqtt
from actuator import actuator_control
from pymongo import MongoClient
import json

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["iot_db"]
collection = db["sensor_data"]

def on_message_full(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    # Store
    collection.insert_one(data)

    # Decision
    actuator_control(data)

    print("Processed:", data)

client = mqtt.Client()
client.connect("localhost", 1883)

client.subscribe("iot/sensor/data")
client.on_message = on_message_full

print("Running full pipeline... Press Ctrl+C to stop.")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped full pipeline.")
    client.disconnect()