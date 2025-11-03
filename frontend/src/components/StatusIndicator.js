import React from 'react';
import '../styles/StatusIndicator.css';

const StatusIndicator = ({ apiStatus, onRefresh }) => {
  const getStatusColor = () => {
    if (apiStatus.status === 'ok' && apiStatus.modelLoaded) return 'success';
    if (apiStatus.status === 'ok' && !apiStatus.modelLoaded) return 'warning';
    return 'error';
  };

  const getStatusText = () => {
    if (apiStatus.status === 'ok' && apiStatus.modelLoaded) {
      return 'Model Ready';
    }
    if (apiStatus.status === 'ok' && !apiStatus.modelLoaded) {
      return 'API Connected - Model Not Loaded';
    }
    return 'API Disconnected';
  };

  return (
    <div className={`status-indicator ${getStatusColor()}`}>
      <div className="status-content">
        <span className="status-dot"></span>
        <span className="status-text">{getStatusText()}</span>
        <button className="refresh-btn" onClick={onRefresh}>
          🔄
        </button>
      </div>
    </div>
  );
};

export default StatusIndicator;

