from fastapi import FastAPI, File, UploadFile
import numpy as np
from tensorflow.keras.models import load_model
import json

# --- NEW: Import CORS Middleware ---
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LINE-SHIELD API")

# --- NEW: Add CORS settings ---
# This allows your frontend (running on localhost:3000) to communicate with your backend.
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- END NEW ---

model = load_model('line_shield_model.h5')
CLASS_NAMES = ['Normal', 'Line-to-Ground Fault', 'Arcing Fault']

def locate_fault_impedance(voltage_phasor, current_phasor, line_reactance_per_km=0.4):
    if current_phasor == 0: return -1
    impedance = abs(voltage_phasor / current_phasor)
    distance = impedance / line_reactance_per_km
    return distance

@app.post("/predict")
async def predict_fault(file: UploadFile = File(...)):
    contents = await file.read()
    data = json.loads(contents)
    waveform = np.array(data['waveform'])

    if waveform.shape[0] != 3000:
        return {"error": f"Invalid waveform length. Expected 3000, got {waveform.shape[0]}"}
    
    waveform_reshaped = waveform.reshape(1, 3000, 1)
    prediction = model.predict(waveform_reshaped)
    predicted_class_index = np.argmax(prediction)
    predicted_class_name = CLASS_NAMES[predicted_class_index]
    confidence = float(np.max(prediction))

    distance_km = -1
    if predicted_class_name != 'Normal':
        v_fault = 220 # Placeholder
        i_fault = 150 # Placeholder
        distance_km = locate_fault_impedance(v_fault, i_fault)

    return {
        "fault_type": predicted_class_name,
        "confidence": f"{confidence:.4f}",
        "estimated_distance_km": f"{distance_km:.2f}" if distance_km != -1 else "N/A"
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to the LINE-SHIELD Prediction API"}