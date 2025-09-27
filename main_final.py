import asyncio
import json
import numpy as np
import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.models import load_model

# --- Configuration ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
# MODIFICATION 1: Use the wildcard to listen to all districts
MQTT_TOPIC = "tn/#" 

# --- FastAPI App Initialization ---
app = FastAPI(title="LINE-SHIELD Real-Time API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = load_model('line_shield_model.h5')
CLASS_NAMES = ['Normal', 'Line-to-Ground Fault', 'Arcing Fault']

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

def setup_mqtt_client():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ MQTT Connected and subscribed to all of Tamil Nadu.")
            client.subscribe(MQTT_TOPIC)
        else:
            print(f"❌ Failed to connect to MQTT, return code {rc}")

    async def on_message_async(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            waveform = np.array(payload['waveform'])
            
            waveform_reshaped = waveform.reshape(1, 3000, 1)
            prediction = model.predict(waveform_reshaped)
            predicted_class_index = np.argmax(prediction)
            
            # MODIFICATION 2: Add lat/lon to the result payload
            result = {
                "transformer_id": payload.get('transformer_id', 'UNKNOWN'),
                "fault_type": CLASS_NAMES[predicted_class_index],
                "confidence": float(np.max(prediction)),
                "lat": payload.get('lat'),
                "lon": payload.get('lon')
            }

            await manager.broadcast(json.dumps(result))
            print(f"Sent prediction from {result['transformer_id']} to dashboard: {result['fault_type']}")

        except Exception as e:
            print(f"Error processing message: {e}")
    
    def on_message(client, userdata, msg):
        asyncio.run(on_message_async(client, userdata, msg))

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

@app.on_event("startup")
def startup_event():
    print("Starting MQTT client in background...")
    mqtt_client = setup_mqtt_client()
    mqtt_client.loop_start()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Dashboard connected.")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Dashboard disconnected.")