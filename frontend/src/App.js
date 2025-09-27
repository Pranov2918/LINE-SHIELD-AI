import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const API_STATUS = {
  CONNECTING: "Connecting...",
  CONNECTED: "Connected | Listening for faults",
  DISCONNECTED: "Disconnected"
};

function App() {
  const [latestFault, setLatestFault] = useState(null);
  const [faultHistory, setFaultHistory] = useState([]);
  const [apiStatus, setApiStatus] = useState(API_STATUS.CONNECTING);
  const mapRef = useRef();

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onopen = () => setApiStatus(API_STATUS.CONNECTED);
    ws.onclose = () => setApiStatus(API_STATUS.DISCONNECTED);

    ws.onmessage = (event) => {
      const faultData = JSON.parse(event.data);
      const newFault = {
        ...faultData,
        position: [faultData.lat, faultData.lon],
        id: Date.now()
      };

      if (newFault.fault_type !== "Normal") {
        setLatestFault(newFault);
        setFaultHistory(prev => [newFault, ...prev.slice(0, 4)]);
        const { current: map } = mapRef;
        if (map && newFault.position[0] && newFault.position[1]) {
          map.flyTo(newFault.position, 14);
        }
      }
    };

    return () => ws.close();
  }, []);

  const getStatusBadgeClass = () => {
      if (apiStatus === API_STATUS.CONNECTED) return 'badge bg-success';
      if (apiStatus === API_STATUS.DISCONNECTED) return 'badge bg-danger';
      return 'badge bg-warning';
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <nav className="navbar navbar-dark bg-dark">
        <div className="container-fluid">
          <a className="navbar-brand" href="#">
            ⚡ LINE-SHIELD Real-Time Dashboard (Tamil Nadu)
          </a>
        </div>
      </nav>

      <div className="container-fluid flex-grow-1" style={{ display: 'flex' }}>
        <div className="row flex-grow-1">

          {/* Control Panel */}
          <div className="col-md-4 col-lg-3 p-3 bg-light border-end">
            <h4 className="mb-3">System Status</h4>
            <h5><span className={getStatusBadgeClass()}>{apiStatus}</span></h5>
            <hr />

            <h4 className="mt-4">Latest Alert</h4>
            {latestFault ? (
              <div className="card text-white bg-danger mt-3">
                <div className="card-header">
                  <strong>{latestFault.fault_type}</strong>
                </div>
                <div className="card-body">
                  <p className="card-text"><strong>Transformer ID:</strong> {latestFault.transformer_id}</p>
                  <p className="card-text"><strong>Confidence:</strong> {latestFault.confidence.toFixed(2)}</p>
                </div>
              </div>
            ) : (
              <div className="card mt-3">
                 <div className="card-body">
                    No faults detected recently.
                 </div>
              </div>
            )}
            <hr />

            <h4 className="mt-4">Fault History</h4>
            <ul className="list-group">
              {faultHistory.map(fault => (
                <li key={fault.id} className="list-group-item">
                  <strong>{fault.transformer_id}:</strong> {fault.fault_type}
                </li>
              ))}
            </ul>
          </div>

          {/* Map View */}
          <div className="col-md-8 col-lg-9 p-0">
            <MapContainer ref={mapRef} center={[11.1271, 78.6569]} zoom={7} style={{ height: '100%', width: '100%' }}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {latestFault && latestFault.position[0] && (
                <>
                  <Marker position={latestFault.position}>
                    <Popup><b>{latestFault.fault_type}</b><br />ID: {latestFault.transformer_id}</Popup>
                  </Marker>
                  <Circle center={latestFault.position} radius={500} color="red" />
                </>
              )}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;