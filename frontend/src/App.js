import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import ManualInput from './components/ManualInput';
import ResultsDisplay from './components/ResultsDisplay';
import Header from './components/Header';
import StatusIndicator from './components/StatusIndicator';
import './styles/App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5050';

function App() {
  const [predictionResults, setPredictionResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState({ status: 'checking', modelLoaded: false });
  const [activeTab, setActiveTab] = useState('file'); // 'file' or 'manual'
  const [featureNames, setFeatureNames] = useState([]);

  useEffect(() => {
    checkApiHealth();
    fetchFeatureNames();
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
    
    // Fallback: Use hardcoded feature list from model metadata
    // This matches the 77 features in model_metadata.json
    const fallbackFeatures = [
      "Protocol", "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
      "Fwd Packets Length Total", "Bwd Packets Length Total", "Fwd Packet Length Max",
      "Fwd Packet Length Min", "Fwd Packet Length Mean", "Fwd Packet Length Std",
      "Bwd Packet Length Max", "Bwd Packet Length Min", "Bwd Packet Length Mean",
      "Bwd Packet Length Std", "Flow Bytes/s", "Flow Packets/s", "Flow IAT Mean",
      "Flow IAT Std", "Flow IAT Max", "Flow IAT Min", "Fwd IAT Total", "Fwd IAT Mean",
      "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min", "Bwd IAT Total", "Bwd IAT Mean",
      "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min", "Fwd PSH Flags", "Bwd PSH Flags",
      "Fwd URG Flags", "Bwd URG Flags", "Fwd Header Length", "Bwd Header Length",
      "Fwd Packets/s", "Bwd Packets/s", "Packet Length Min", "Packet Length Max",
      "Packet Length Mean", "Packet Length Std", "Packet Length Variance",
      "FIN Flag Count", "SYN Flag Count", "RST Flag Count", "PSH Flag Count",
      "ACK Flag Count", "URG Flag Count", "CWE Flag Count", "ECE Flag Count",
      "Down/Up Ratio", "Avg Packet Size", "Avg Fwd Segment Size",
      "Avg Bwd Segment Size", "Fwd Avg Bytes/Bulk", "Fwd Avg Packets/Bulk",
      "Fwd Avg Bulk Rate", "Bwd Avg Bytes/Bulk", "Bwd Avg Packets/Bulk",
      "Bwd Avg Bulk Rate", "Subflow Fwd Packets", "Subflow Fwd Bytes",
      "Subflow Bwd Packets", "Subflow Bwd Bytes", "Init Fwd Win Bytes",
      "Init Bwd Win Bytes", "Fwd Act Data Packets", "Fwd Seg Size Min",
      "Active Mean", "Active Std", "Active Max", "Active Min",
      "Idle Mean", "Idle Std", "Idle Max", "Idle Min"
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

