import pandas as pd
from pymongo import MongoClient
import json

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["iot_db"]
collection = db["sensor_data"]
data = list(collection.find())
df = pd.DataFrame(data)

print(df[['temperature', 'humidity']].tail(10))

import matplotlib.pyplot as plt

plt.plot(df['temperature'], label='Temperature')
plt.plot(df['humidity'], label='Humidity')
plt.legend()
plt.title("Sensor Data Trends")
plt.xlabel("Index")
plt.ylabel("Value")
plt.show()