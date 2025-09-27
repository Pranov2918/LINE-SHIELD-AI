import paho.mqtt.client as mqtt
import pandas as pd
import time
import json
import random

# --- Configuration ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# --- SIMULATED SENSOR LOCATIONS ACROSS TAMIL NADU ---
SENSORS = [
    {"district": "dharmapuri", "city": "nalampalli", "id": "TR-DMP-404", "lat": 12.09, "lon": 78.16},
    {"district": "chennai", "city": "adyar", "id": "TR-CHN-101", "lat": 13.00, "lon": 80.25},
    {"district": "coimbatore", "city": "gandhipuram", "id": "TR-CBE-215", "lat": 11.01, "lon": 76.97},
    {"district": "madurai", "city": "simmakkal", "id": "TR-MDU-330", "lat": 9.92, "lon": 78.12}
]

# --- Load Data ---
print("Loading waveform data for simulation...")
df = pd.read_csv('fault_data.csv')

def run_simulation():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("✅ Connected to MQTT Broker as a multi-location publisher.")
    except Exception as e:
        print(f"❌ Could not connect to MQTT Broker: {e}")
        return

    client.loop_start()
    print("--- Publishing data from random locations every 5 seconds. Press Ctrl+C to stop. ---")

    try:
        while True:
            # Pick a random sensor and a random waveform to send
            sensor = random.choice(SENSORS)
            row = df.sample(n=1).iloc[0]
            
            waveform = row.drop('label').tolist()
            
            # Construct the dynamic MQTT topic
            topic = f"tn/{sensor['district']}/{sensor['city']}/{sensor['id']}"
            
            payload = {
                "timestamp": time.time(),
                "transformer_id": sensor['id'],
                "lat": sensor['lat'],
                "lon": sensor['lon'],
                "waveform": waveform
            }
            
            result = client.publish(topic, json.dumps(payload))
            
            if result[0] == 0:
                print(f"📤 Sent data from {sensor['district'].upper()} (ID: {sensor['id']})")
            else:
                print(f"Failed to send message to topic {topic}")
                
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    run_simulation()