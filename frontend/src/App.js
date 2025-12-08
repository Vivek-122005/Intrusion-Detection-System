import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import ManualInput from './components/ManualInput';
import ResultsDisplay from './components/ResultsDisplay';
import Header from './components/Header';
import StatusIndicator from './components/StatusIndicator';
import LiveAlerts from './components/LiveAlerts';
import MinimalLiveDashboard from './components/MinimalLiveDashboard';
import { setNavigateToTab } from './components/MinimalLiveDashboard';
import './styles/App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';

function App() {
  const [predictionResults, setPredictionResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState({ status: 'checking', modelLoaded: false });
  const [activeTab, setActiveTab] = useState('file'); // 'file', 'manual', or 'live'
  const [featureNames, setFeatureNames] = useState([]);

  useEffect(() => {
    checkApiHealth();
    fetchFeatureNames();
    // Set up navigation function for MinimalLiveDashboard
    setNavigateToTab(setActiveTab);
  }, []);

  const fetchFeatureNames = async () => {
    try {
      // Try to get feature names from metadata endpoint
      const response = await fetch(`${API_BASE_URL}/api/metadata`, {
        method: 'GET',
        mode: 'cors',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.feature_names && data.feature_names.length > 0) {
          setFeatureNames(data.feature_names);
          return;
        }
      }
    } catch (err) {
      console.log('Metadata endpoint not available, trying fallback', err);
    }
    
    // Fallback: Use the 30 live-extractable features from model_metadata.json
    const fallbackFeatures = [
      "Protocol",
      "Flow Duration",
      "Total Fwd Packets",
      "Fwd Packets Length Total",
      "Fwd Packet Length Max",
      "Fwd Packet Length Min",
      "Fwd Packet Length Mean",
      "Fwd Packet Length Std",
      "Flow Bytes/s",
      "Flow Packets/s",
      "Flow IAT Mean",
      "Flow IAT Std",
      "Flow IAT Max",
      "Flow IAT Min",
      "Fwd IAT Total",
      "Fwd IAT Mean",
      "Fwd IAT Std",
      "Fwd IAT Max",
      "Fwd IAT Min",
      "Fwd Packets/s",
      "Packet Length Min",
      "Packet Length Max",
      "Packet Length Mean",
      "Packet Length Std",
      "Packet Length Variance",
      "Avg Packet Size",
      "Avg Fwd Segment Size",
      "Subflow Fwd Packets",
      "Subflow Fwd Bytes",
      "Fwd Act Data Packets"
    ];
    setFeatureNames(fallbackFeatures);
  };

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`, {
        method: "GET",
        mode: "cors",
        credentials: "include",
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      // Convert snake_case to camelCase for consistency
      setApiStatus({
        status: data.status || 'error',
        modelLoaded: data.model_loaded || data.modelLoaded || false,
        labelEncoderLoaded: data.label_encoder_loaded || data.labelEncoderLoaded || false
      });
    } catch (err) {
      console.error('Health check error:', err);
      setApiStatus({ status: 'error', modelLoaded: false });
    }
  };

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    setPredictionResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Prediction failed');
      }

      const data = await response.json();
      setPredictionResults(data);
    } catch (err) {
      setError(err.message || 'An error occurred during prediction');
    } finally {
      setLoading(false);
    }
  };

  const handleManualPredict = async (dataArray, featureNamesParam) => {
    setLoading(true);
    setError(null);
    setPredictionResults(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/predict-batch`, {
        method: 'POST',
        mode: 'cors',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: dataArray,
          feature_names: (featureNamesParam && featureNamesParam.length > 0)
            ? featureNamesParam
            : (featureNames && featureNames.length > 0 ? featureNames : undefined)
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Prediction failed');
      }

      const data = await response.json();
      if (data.debug) {
        console.debug('Backend debug info:', data.debug);
      }
      
      // Format response to match ResultsDisplay expectations
      const formattedData = {
        success: true,
        total_samples: data.predictions ? data.predictions.length : 1,
        predictions: data.predictions || [],
        prediction_counts: data.predictions ? 
          data.predictions.reduce((acc, pred) => {
            acc[pred] = (acc[pred] || 0) + 1;
            return acc;
          }, {}) : {},
        statistics: {
          benign_count: data.predictions ? 
            data.predictions.filter(p => p === 'Benign').length : 0,
          attack_count: data.predictions ? 
            data.predictions.filter(p => p !== 'Benign').length : 0,
          attack_percentage: data.predictions ? 
            (data.predictions.filter(p => p !== 'Benign').length / data.predictions.length * 100) : 0,
        },
        classes: data.classes || [],
      };
      
      setPredictionResults(formattedData);
    } catch (err) {
      setError(err.message || 'An error occurred during prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <Header />
      <div className="container">
        <StatusIndicator apiStatus={apiStatus} onRefresh={checkApiHealth} />
        
        <div className="main-content">
          {/* Tab Navigation */}
          <div className="tabs-container">
            <button
              className={`tab-button ${activeTab === 'file' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('file');
                setPredictionResults(null);
                setError(null);
              }}
            >
              📁 File Upload
            </button>
            <button
              className={`tab-button ${activeTab === 'manual' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('manual');
                setPredictionResults(null);
                setError(null);
              }}
            >
              📝 Manual Input
            </button>
            <button
              className={`tab-button ${activeTab === 'live' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('live');
                setPredictionResults(null);
                setError(null);
              }}
            >
              🔴 Live Alerts
            </button>
          </div>

          {/* Tab Content */}
          <div className="tab-content">
            {activeTab === 'file' && (
          <div className="upload-section">
            <FileUpload 
              onFileUpload={handleFileUpload} 
              loading={loading}
              disabled={!apiStatus.modelLoaded}
            />
              </div>
            )}

            {activeTab === 'manual' && (
              <div className="manual-section">
                <ManualInput
                  onPredict={handleManualPredict}
                  loading={loading}
                  disabled={!apiStatus.modelLoaded}
                  featureNames={featureNames}
                />
              </div>
            )}

            {activeTab === 'live' && (
              <div className="live-section">
                <LiveAlerts onNavigate={setActiveTab} />
              </div>
            )}
          </div>

            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            )}

          {predictionResults && (
            <ResultsDisplay results={predictionResults} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

