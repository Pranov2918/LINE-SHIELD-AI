## 🎯 The Problem
In power distribution networks, especially in dense areas like those in Tamil Nadu, Low-Tension (LT) line faults such as line breaks or arcing can go undetected by traditional systems. These failures lead to public safety hazards (electrocution, fire), economic losses from power outages, and slow manual restoration processes.

## 🚀 Our Solution
LINE-SHIELD is a software-first solution that addresses these challenges by:

Continuously monitoring electrical waveform data (voltage and current).

Using a trained AI model (1D-CNN) to instantly classify different types of faults, including those missed by normal circuit breakers.

Broadcasting live alerts to a centralized dashboard.

Pinpointing the fault location on a GIS map, enabling rapid response from repair crews.

## 🛠️ System Architecture
The project operates in three parts that communicate in real time:

Sensor Simulator (stream_simulator.py): A Python script that mimics multiple hardware sensors across Tamil Nadu. It reads sample waveform data and publishes it to a central MQTT broker.

AI Backend (main_final.py): A FastAPI server that subscribes to the MQTT broker. When a message arrives, it processes the waveform with the TensorFlow/Keras model and, if a fault is detected, pushes an alert via WebSockets.

Real-Time Dashboard (React Frontend): A React application that establishes a WebSocket connection to the backend. It listens for alerts and instantly updates the map and UI with the fault type, location, and confidence score.

## ✨ Key Features
Real-Time Fault Classification: Identifies Normal, Line-to-Ground, and Arcing faults.

Live GIS Mapping: Instantly visualizes the location of new faults.

Scalable MQTT Architecture: Designed to handle data from thousands of sensors.

WebSocket-Powered Dashboard: No need to refresh the page for live updates.

Professional UI: A clean and intuitive user interface built with Bootstrap.

## 💻 Technology Stack
Backend: Python, FastAPI, TensorFlow (Keras)

Real-Time Communication: Paho-MQTT, WebSockets

Frontend: React.js, Bootstrap 5, Leaflet.js (for maps)

Data Science: Pandas, NumPy, Scikit-learn

## 🔧 Setup and Running the Project
To run this project locally, you will need three separate terminals.

Prerequisites:
Git

Python 3.9+

Node.js and npm

1. Setup:

# Clone the repository
git clone https://github.com/Pranov2918/LINE-SHIELD-AI.git
cd LINE-SHIELD-AI

# Setup Backend
pip install -r requirements.txt

# Setup Frontend
cd frontend
npm install
cd ..
2. Run the Application:
Terminal 1: Start the Backend


# In the main LINE-SHIELD-AI folder
uvicorn main_final:app
Terminal 2: Start the Frontend


# In the /frontend folder
npm start
Terminal 3: Start the Sensor Simulator


# In the main LINE-SHIELD-AI folder
python stream_simulator.py
Now, open your browser to http://localhost:3000 to see the live dashboard.
