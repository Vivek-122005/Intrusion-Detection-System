import React, { useState, useEffect } from 'react';
import './MinimalLiveDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';

// Navigation function passed from parent
let navigateToTab = null;
export const setNavigateToTab = (fn) => {
  navigateToTab = fn;
};

function MinimalLiveDashboard({ onNavigate }) {
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
  },
  'Benign': {
    color: '#4CAF50',
    icon: '✅',
    description: 'Normal network traffic'
  }
};

  const [alerts, setAlerts] = useState([]);
  const [isPolling, setIsPolling] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    benign: 0,
    attacks: 0,
    lastUpdate: null
  });

  useEffect(() => {
    if (isPolling) {
      const interval = setInterval(() => {
        fetchAlerts();
      }, 2000); // Poll every 2 seconds

      return () => clearInterval(interval);
    }
  }, [isPolling]);

  useEffect(() => {
    // Update stats when alerts change
    const benignCount = alerts.filter(a => a.label === 'Benign').length;
    const attackCount = alerts.filter(a => a.label !== 'Benign').length;
    setStats({
      total: alerts.length,
      benign: benignCount,
      attacks: attackCount,
      lastUpdate: alerts.length > 0 ? alerts[alerts.length - 1].timestamp : null
    });
  }, [alerts]);

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/latest-alerts?n=100`, {
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
    }
  };

  const getAttackConfig = (label) => {
    return ATTACK_CONFIG[label] || {
      color: '#757575',
      icon: '⚠️',
      description: 'Unknown threat detected'
    };
  };

  const handleAlertClick = (alert) => {
    if (alert.label !== 'Benign') {
      setSelectedAlert(alert);
      setShowDetails(true);
      // Features are already in the alert if available
      if (alert.features) {
        setAlertFeatures(alert.features);
      } else {
        setAlertFeatures(null);
      }
    }
  };

  const [alertFeatures, setAlertFeatures] = useState(null);

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString();
  };

  // Get only attack alerts (non-Benign)
  const attackAlerts = alerts.filter(a => a.label !== 'Benign').reverse();

  return (
    <div className="minimal-dashboard">
      {/* Header Bar */}
      <div className="minimal-header">
        <div className="header-left">
          <h1 className="dashboard-title-minimal">
            <span className="shield-icon">🛡️</span>
            Live IDS
          </h1>
          <div className="status-indicator-minimal">
            <div className={`status-dot ${isPolling ? 'active' : 'inactive'}`}></div>
            <span>{isPolling ? 'Monitoring' : 'Stopped'}</span>
          </div>
        </div>
        <div className="header-right">
          <div className="stats-minimal">
            <div className="stat-item-minimal">
              <span className="stat-value">{stats.attacks}</span>
              <span className="stat-label">Threats</span>
            </div>
            <div className="stat-item-minimal">
              <span className="stat-value">{stats.benign}</span>
              <span className="stat-label">Benign</span>
            </div>
            <div className="stat-item-minimal">
              <span className="stat-value">{stats.total}</span>
              <span className="stat-label">Total</span>
            </div>
          </div>
          <div className="nav-buttons-minimal">
            <button
              className="nav-btn-minimal"
              onClick={() => {
                if (onNavigate) {
                  onNavigate('file');
                } else if (navigateToTab) {
                  navigateToTab('file');
                }
              }}
              title="Upload CSV"
            >
              📁 Upload CSV
            </button>
            <button
              className="nav-btn-minimal"
              onClick={() => {
                if (onNavigate) {
                  onNavigate('manual');
                } else if (navigateToTab) {
                  navigateToTab('manual');
                }
              }}
              title="Manual Input"
            >
              📝 Manual Input
            </button>
          </div>
          <button
            className={`control-btn-minimal ${isPolling ? 'stop' : 'start'}`}
            onClick={togglePolling}
          >
            {isPolling ? '⏸ Stop' : '▶ Start'}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="minimal-content">
        {attackAlerts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h2>No Threats Detected</h2>
            <p>{isPolling ? 'Monitoring network traffic...' : 'Click Start to begin monitoring'}</p>
          </div>
        ) : (
          <div className="alerts-grid">
            {attackAlerts.map((alert, index) => {
              const config = getAttackConfig(alert.label);
              return (
                <div
                  key={index}
                  className="alert-card"
                  style={{ borderLeftColor: config.color }}
                  onClick={() => handleAlertClick(alert)}
                >
                  <div className="alert-card-header">
                    <span className="alert-icon">{config.icon}</span>
                    <span className="alert-type">{alert.label}</span>
                    <span className="alert-confidence">
                      {(alert.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="alert-card-body">
                    <div className="alert-time">
                      {formatTimestamp(alert.timestamp)}
                    </div>
                    <div className="alert-flow-minimal">
                      {alert.flow}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Attack Details Modal */}
      {showDetails && selectedAlert && (
        <div className="modal-overlay" onClick={() => setShowDetails(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <span className="modal-icon">{getAttackConfig(selectedAlert.label).icon}</span>
                {selectedAlert.label} Attack Details
              </h2>
              <button className="close-btn" onClick={() => setShowDetails(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-section">
                <h3>Attack Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Attack Type:</span>
                    <span className="detail-value">{selectedAlert.label}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Confidence:</span>
                    <span className="detail-value">{(selectedAlert.confidence * 100).toFixed(2)}%</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Date:</span>
                    <span className="detail-value">{formatDate(selectedAlert.timestamp)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Time:</span>
                    <span className="detail-value">{formatTimestamp(selectedAlert.timestamp)}</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h3>Flow Information</h3>
                <div className="flow-details">
                  <pre>{selectedAlert.flow}</pre>
                </div>
              </div>

              <div className="detail-section">
                <h3>Description</h3>
                <p>{getAttackConfig(selectedAlert.label).description}</p>
              </div>

              {alertFeatures && (
                <div className="detail-section">
                  <h3>Feature Values ({Object.keys(alertFeatures).length} features)</h3>
                  <div className="features-list">
                    {Object.entries(alertFeatures)
                      .sort(([a], [b]) => a.localeCompare(b))
                      .map(([key, value]) => {
                        // Format value nicely
                        let displayValue = value;
                        if (typeof value === 'number') {
                          if (value === 0) {
                            displayValue = '0';
                          } else if (Math.abs(value) < 0.0001) {
                            displayValue = value.toExponential(2);
                          } else if (Math.abs(value) >= 1000) {
                            displayValue = value.toLocaleString('en-US', { maximumFractionDigits: 2 });
                          } else {
                            displayValue = value.toFixed(4);
                          }
                        }
                        return (
                          <div key={key} className="feature-item">
                            <span className="feature-key">{key}:</span>
                            <span className="feature-value">{displayValue}</span>
                          </div>
                        );
                      })}
                  </div>
                </div>
              )}
              {!alertFeatures && (
                <div className="detail-section">
                  <p style={{ color: 'rgba(255, 255, 255, 0.5)', fontStyle: 'italic' }}>
                    Feature details not available for this alert
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MinimalLiveDashboard;

