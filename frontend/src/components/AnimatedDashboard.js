import React, { useState, useEffect, useRef } from 'react';
import './AnimatedDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';

// Attack type configurations
const ATTACK_CONFIG = {
  'Bruteforce': {
    color: '#E91E63',
    icon: '🔐',
    description: 'Multiple rapid connection attempts detected'
  },
  'DDoS': {
    color: '#F44336',
    icon: '🌊',
    description: 'Distributed Denial of Service attack'
  },
  'DoS': {
    color: '#FF9800',
    icon: '⚡',
    description: 'Denial of Service attack detected'
  },
  'Bot': {
    color: '#9C27B0',
    icon: '🤖',
    description: 'Botnet activity detected'
  },
  'Infiltration': {
    color: '#FF5722',
    icon: '🕵️',
    description: 'Unauthorized access attempt'
  },
  'Web Attack': {
    color: '#2196F3',
    icon: '🌐',
    description: 'Web application attack detected'
  }
};

function AnimatedDashboard() {
  const [alerts, setAlerts] = useState([]);
  const [isPolling, setIsPolling] = useState(false);
  const [scene, setScene] = useState('calm'); // calm, suspicious, attack, resolved
  const [currentAttack, setCurrentAttack] = useState(null);
  const [previousAlertCount, setPreviousAlertCount] = useState(0);
  const sceneTimeoutRef = useRef(null);

  useEffect(() => {
    if (isPolling) {
      const interval = setInterval(() => {
        fetchAlerts();
      }, 2000); // Poll every 2 seconds for smoother animations

      return () => clearInterval(interval);
    }
  }, [isPolling]);

  useEffect(() => {
    // Determine scene based on alerts
    if (alerts.length === 0 && isPolling) {
      setScene('calm');
      setCurrentAttack(null);
    } else if (alerts.length > previousAlertCount && alerts.length > 0) {
      // New alert detected
      const latestAlert = alerts[alerts.length - 1];
      if (latestAlert.label !== 'Benign') {
        setScene('attack');
        setCurrentAttack(latestAlert);
        
        // Auto-transition to resolved after 5 seconds
        if (sceneTimeoutRef.current) {
          clearTimeout(sceneTimeoutRef.current);
        }
        sceneTimeoutRef.current = setTimeout(() => {
          setScene('resolved');
          setTimeout(() => {
            setScene('calm');
            setCurrentAttack(null);
          }, 3000);
        }, 5000);
      } else {
        setScene('suspicious');
        setTimeout(() => setScene('calm'), 2000);
      }
    } else if (alerts.length > 0 && alerts.length === previousAlertCount) {
      // No new alerts, but alerts exist
      const hasAttack = alerts.some(a => a.label !== 'Benign');
      if (hasAttack && scene === 'calm') {
        setScene('suspicious');
      }
    }
    
    setPreviousAlertCount(alerts.length);
  }, [alerts, isPolling, previousAlertCount, scene]);

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/latest-alerts?n=10`, {
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
      }
    } catch (err) {
      console.error('Error fetching alerts:', err);
    }
  };

  const togglePolling = () => {
    setIsPolling(!isPolling);
    if (!isPolling) {
      fetchAlerts();
      setScene('calm');
      setCurrentAttack(null);
    }
  };

  const getAttackConfig = (label) => {
    return ATTACK_CONFIG[label] || {
      color: '#757575',
      icon: '⚠️',
      description: 'Unknown threat detected'
    };
  };

  return (
    <div className={`animated-dashboard scene-${scene}`}>
      {/* Background Animation Layer */}
      <div className="background-animation">
        {[...Array(20)].map((_, i) => (
          <div key={i} className={`packet packet-${i}`} />
        ))}
      </div>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Header */}
        <div className="dashboard-header">
          <h1 className="dashboard-title">
            <span className="pulse-icon">🛡️</span>
            Live Intrusion Detection System
          </h1>
          <button
            className={`control-button ${isPolling ? 'active' : ''}`}
            onClick={togglePolling}
          >
            {isPolling ? '⏸️ Stop Monitoring' : '▶️ Start Monitoring'}
          </button>
        </div>

        {/* Scene 1: Calm Network State */}
        {scene === 'calm' && (
          <div className="scene-calm">
            <div className="status-indicator calm">
              <div className="heartbeat-line"></div>
            </div>
            <h2 className="scene-title">Monitoring live network traffic...</h2>
            <p className="scene-message">Everything looks normal 😊</p>
            <div className="stats">
              <div className="stat-item">
                <span className="stat-value">{alerts.length}</span>
                <span className="stat-label">Total Alerts</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">
                  {alerts.filter(a => a.label === 'Benign').length}
                </span>
                <span className="stat-label">Benign Flows</span>
              </div>
            </div>
          </div>
        )}

        {/* Scene 2: Suspicious Activity */}
        {scene === 'suspicious' && (
          <div className="scene-suspicious">
            <div className="status-indicator suspicious">
              <div className="warning-pulse"></div>
            </div>
            <h2 className="scene-title">⚠️ Unusual packet activity detected...</h2>
            <p className="scene-message">Analyzing network patterns...</p>
          </div>
        )}

        {/* Scene 3: Attack Detected */}
        {scene === 'attack' && currentAttack && (
          <div className="scene-attack">
            <div className="attack-animation">
              <div className="lightning-bolt">⚡</div>
              <div className="breaking-glass"></div>
            </div>
            <div className="attack-alert">
              <h2 className="attack-title">🚨 INTRUSION DETECTED!</h2>
              <div className="attack-details">
                <div className="attack-type">
                  <span className="attack-icon">
                    {getAttackConfig(currentAttack.label).icon}
                  </span>
                  <span className="attack-name">{currentAttack.label}</span>
                </div>
                <div className="attack-confidence">
                  Confidence: <strong>{(currentAttack.confidence * 100).toFixed(1)}%</strong>
                </div>
                <div className="attack-description">
                  {getAttackConfig(currentAttack.label).description}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Scene 4: System Response */}
        {scene === 'resolved' && (
          <div className="scene-resolved">
            <div className="success-indicator">
              <div className="checkmark">✓</div>
            </div>
            <h2 className="scene-title">✅ Threat Successfully Identified</h2>
            <p className="scene-message">Attack logged and network secured.</p>
            {currentAttack && (
              <div className="resolved-details">
                <p>Attack Type: <strong>{currentAttack.label}</strong></p>
                <p>Confidence: <strong>{(currentAttack.confidence * 100).toFixed(1)}%</strong></p>
              </div>
            )}
          </div>
        )}

        {/* Alert History (always visible at bottom) */}
        <div className="alert-history">
          <h3>Recent Alerts</h3>
          <div className="alert-list">
            {alerts.length === 0 ? (
              <div className="no-alerts">
                {isPolling ? 'Waiting for network activity...' : 'Start monitoring to see alerts'}
              </div>
            ) : (
              alerts.slice().reverse().slice(0, 5).map((alert, index) => (
                <div
                  key={index}
                  className="alert-mini"
                  style={{
                    borderLeftColor: alert.label === 'Benign' 
                      ? '#4CAF50' 
                      : getAttackConfig(alert.label).color
                  }}
                >
                  <span className="alert-mini-label">{alert.label}</span>
                  {alert.confidence && (
                    <span className="alert-mini-confidence">
                      {(alert.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnimatedDashboard;

