import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print("Received:", data)

    # Edge Processing Logic
    if data["temperature"] > 30:
        print("⚠️ ALERT: High Temperature!")

client = mqtt.Client()
client.connect("localhost", 1883)

client.subscribe("iot/sensor/data")
client.on_message = on_message

print("Listening for messages... Press Ctrl+C to stop.")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Stopped subscriber.")
    client.disconnect()