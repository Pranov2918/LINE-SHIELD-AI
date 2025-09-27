import paho.mqtt.client as mqtt
import json
import numpy as np
from tensorflow.keras.models import load_model

# --- Configuration ---
MQTT_BROKER = "broker.hivemq.com" # Using a free, public broker for testing
MQTT_PORT = 1883
MQTT_TOPIC = "tn/dharmapuri/lt/transformer/data"

# --- Load AI Model (make sure the .h5 file is in the same folder) ---
print("🧠 Loading AI model...")
model = load_model('line_shield_model.h5')
CLASS_NAMES = ['Normal', 'Line-to-Ground Fault', 'Arcing Fault'] # Update if you have more classes
print("✅ Model loaded successfully.")

# --- MQTT Callback Functions ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to MQTT Broker at {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"👂 Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"❌ Failed to connect to MQTT, return code {rc}\n")

def on_message(client, userdata, msg):
    """This function runs every time a new message arrives."""
    print(f"--- ⚡ Message received on topic {msg.topic} ---")
    try:
        payload = json.loads(msg.payload.decode())
        waveform = np.array(payload['waveform'])
        transformer_id = payload.get('transformer_id', 'UNKNOWN_ID')

        if waveform.shape[0] == 3000:
            waveform_reshaped = waveform.reshape(1, 3000, 1)
            prediction = model.predict(waveform_reshaped)
            predicted_class_index = np.argmax(prediction)
            predicted_class_name = CLASS_NAMES[predicted_class_index]
            confidence = float(np.max(prediction))

            print(f"    - Transformer ID: {transformer_id}")
            print(f"    - Prediction Result: '{predicted_class_name}' (Confidence: {confidence:.2f})")

            if predicted_class_name != 'Normal':
                print(f"    🚨 ALERT! Fault detected at Transformer {transformer_id}!")
        else:
            print(f"    ⚠️ Warning: Received waveform with incorrect length.")

    except Exception as e:
        print(f"    ❌ An error occurred during processing: {e}")

# --- Main Execution Logic ---
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# This is a blocking loop that keeps the script listening for messages
client.loop_forever()