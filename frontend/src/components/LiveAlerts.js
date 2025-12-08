import React, { useState, useEffect } from 'react';
import AnimatedDashboard from './AnimatedDashboard';
import './LiveAlerts.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';

function LiveAlerts() {
  const [useAnimated, setUseAnimated] = useState(true);

  // Use animated dashboard by default
  if (useAnimated) {
    return (
      <div>
        <div style={{ textAlign: 'right', marginBottom: '10px' }}>
          <button
            onClick={() => setUseAnimated(false)}
            style={{
              padding: '8px 16px',
              background: '#666',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Switch to List View
          </button>
        </div>
        <AnimatedDashboard />
      </div>
    );
  }

  // Original list view
  return (
    <div>
      <div style={{ textAlign: 'right', marginBottom: '10px' }}>
        <button
          onClick={() => setUseAnimated(true)}
          style={{
            padding: '8px 16px',
            background: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Switch to Animated Dashboard
        </button>
      </div>
      <LiveAlertsList />
    </div>
  );
}

function LiveAlertsList() {
  const [alerts, setAlerts] = useState([]);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isPolling) {
      const interval = setInterval(() => {
        fetchAlerts();
      }, 3000); // Poll every 3 seconds

      return () => clearInterval(interval);
    }
  }, [isPolling]);

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/latest-alerts?n=50`, {
        method: 'GET',
        mode: 'cors',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data.success) {
        setAlerts(data.alerts || []);
        setError(null);
      }
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError(err.message);
    }
  };

  const togglePolling = () => {
    setIsPolling(!isPolling);
    if (!isPolling) {
      fetchAlerts(); // Fetch immediately when starting
    }
  };

  const getLabelColor = (label) => {
    const colors = {
      'Benign': '#4CAF50',
      'DDoS': '#F44336',
      'DoS': '#FF9800',
      'Bruteforce': '#E91E63',
      'Bot': '#9C27B0',
      'Infiltration': '#FF5722',
      'Web Attack': '#2196F3'
    };
    return colors[label] || '#757575';
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };

  return (
    <div className="live-alerts-container">
      <div className="live-alerts-header">
        <h2>🔴 Live IDS Alerts</h2>
        <button
          className={`poll-button ${isPolling ? 'active' : ''}`}
          onClick={togglePolling}
        >
          {isPolling ? '⏸️ Stop' : '▶️ Start'} Polling
        </button>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ Error: {error}
        </div>
      )}

      <div className="alerts-stats">
        <span>Total Alerts: {alerts.length}</span>
        {alerts.length > 0 && (
          <span>
            Latest: {formatTimestamp(alerts[alerts.length - 1].timestamp)}
          </span>
        )}
      </div>

      <div className="alerts-list">
        {alerts.length === 0 ? (
          <div className="no-alerts">
            {isPolling ? 'No alerts yet. Waiting for network activity...' : 'Click "Start Polling" to begin monitoring'}
          </div>
        ) : (
          alerts.slice().reverse().map((alert, index) => (
            <div
              key={index}
              className="alert-item"
              style={{ borderLeftColor: getLabelColor(alert.label) }}
            >
              <div className="alert-header">
                <span
                  className="alert-label"
                  style={{ backgroundColor: getLabelColor(alert.label) }}
                >
                  {alert.label}
                </span>
                <span className="alert-time">
                  {formatTimestamp(alert.timestamp)}
                </span>
              </div>
              <div className="alert-flow">
                Flow: {alert.flow}
              </div>
              {alert.confidence && (
                <div className="alert-confidence">
                  Confidence: {(alert.confidence * 100).toFixed(2)}%
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default LiveAlerts;

