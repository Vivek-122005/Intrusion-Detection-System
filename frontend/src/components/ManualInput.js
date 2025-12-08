import React, { useState, useEffect } from 'react';
import '../styles/ManualInput.css';

// Feature groups for the 30 live-extractable features only
const FEATURE_GROUPS = {
  'Basic Flow Information': [
    'Protocol',
    'Flow Duration',
    'Total Fwd Packets',
  ],
  'Forward Packet Statistics': [
    'Fwd Packets Length Total',
    'Fwd Packet Length Max',
    'Fwd Packet Length Min',
    'Fwd Packet Length Mean',
    'Fwd Packet Length Std',
    'Fwd Packets/s',
    'Avg Fwd Segment Size',
    'Subflow Fwd Packets',
    'Subflow Fwd Bytes',
    'Fwd Act Data Packets',
  ],
  'Flow Statistics': [
    'Flow Bytes/s',
    'Flow Packets/s',
    'Flow IAT Mean',
    'Flow IAT Std',
    'Flow IAT Max',
    'Flow IAT Min',
  ],
  'Forward IAT (Inter-Arrival Time)': [
    'Fwd IAT Total',
    'Fwd IAT Mean',
    'Fwd IAT Std',
    'Fwd IAT Max',
    'Fwd IAT Min',
  ],
  'Packet Statistics': [
    'Packet Length Min',
    'Packet Length Max',
    'Packet Length Mean',
    'Packet Length Std',
    'Packet Length Variance',
    'Avg Packet Size',
  ],
};

const ManualInput = ({ onPredict, loading, disabled, featureNames }) => {
  const [formData, setFormData] = useState({});
  const [sampleIndex, setSampleIndex] = useState(0);
  const [expectedLabel, setExpectedLabel] = useState('');
  const [activeGroup, setActiveGroup] = useState('Basic Flow Information');
  const [unmatchedKeys, setUnmatchedKeys] = useState([]);

  // Initialize form data with default values (0)
  useEffect(() => {
    if (featureNames && featureNames.length > 0) {
      const initialData = {};
      featureNames.forEach(feature => {
        initialData[feature] = '0';
      });
      setFormData(initialData);
    }
  }, [featureNames]);

  // Organize features into groups
  const organizeFeatures = () => {
    if (!featureNames || featureNames.length === 0) return FEATURE_GROUPS;

    const organized = {};
    const usedFeatures = new Set();

    // First, organize known groups
    Object.keys(FEATURE_GROUPS).forEach(groupName => {
      organized[groupName] = FEATURE_GROUPS[groupName].filter(f => featureNames.includes(f));
      FEATURE_GROUPS[groupName].forEach(f => usedFeatures.add(f));
    });

    // Add remaining features to "Other" group
    const remaining = featureNames.filter(f => !usedFeatures.has(f));
    if (remaining.length > 0) {
      organized['Other Features'] = remaining;
    }

    return organized;
  };

  const handleInputChange = (feature, value) => {
    setFormData(prev => ({
      ...prev,
      [feature]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Convert form data to array format expected by backend
    // Backend expects: { data: [[val1, val2, ...]], feature_names: [...] }
    // We need to maintain the order of featureNames
    if (!featureNames || featureNames.length === 0) {
      alert('Feature names not loaded. Please wait and try again.');
      return;
    }
    
    // Create array of values in the same order as featureNames
    const valuesArray = featureNames.map(feature => 
      parseFloat(formData[feature]) || 0
    );
    
    // Backend expects array of arrays (one sample)
    const dataArray = [valuesArray];
    
    onPredict(dataArray, featureNames);
  };

  const handleReset = () => {
    const resetData = {};
    featureNames.forEach(feature => {
      resetData[feature] = '0';
    });
    setFormData(resetData);
  };

  const handleFillSample = () => {
    // Sample data using only the 30 live-extractable features
    const samples = [
      {
        // 1) Benign - Only 30 features
        'Protocol': '6',
        'Flow Duration': '1832',
        'Total Fwd Packets': '5',
        'Fwd Packets Length Total': '935',
        'Fwd Packet Length Max': '935',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '187',
        'Fwd Packet Length Std': '418.1447',
        'Flow Bytes/s': '673580.8',
        'Flow Packets/s': '3820.9607',
        'Flow IAT Mean': '305.33334',
        'Flow IAT Std': '373.90622',
        'Flow IAT Max': '935',
        'Flow IAT Min': '6',
        'Fwd IAT Total': '1832',
        'Fwd IAT Mean': '458',
        'Fwd IAT Std': '587.34033',
        'Fwd IAT Max': '1258',
        'Fwd IAT Min': '6',
        'Fwd Packets/s': '2729.2576',
        'Packet Length Min': '0',
        'Packet Length Max': '935',
        'Packet Length Mean': '154.25',
        'Packet Length Std': '332.36844',
        'Packet Length Variance': '110468.79',
        'Avg Packet Size': '176.28572',
        'Avg Fwd Segment Size': '187',
        'Subflow Fwd Packets': '5',
        'Subflow Fwd Bytes': '935',
        'Fwd Act Data Packets': '1'
      },
      {
        // 2) DoS attacks-Hulk - Only 30 features
        'Protocol': '6',
        'Flow Duration': '11236',
        'Total Fwd Packets': '2',
        'Fwd Packets Length Total': '0',
        'Fwd Packet Length Max': '0',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '0',
        'Fwd Packet Length Std': '0',
        'Flow Bytes/s': '0',
        'Flow Packets/s': '177.99928',
        'Flow IAT Mean': '11236',
        'Flow IAT Std': '0',
        'Flow IAT Max': '11236',
        'Flow IAT Min': '11236',
        'Fwd IAT Total': '11236',
        'Fwd IAT Mean': '11236',
        'Fwd IAT Std': '0',
        'Fwd IAT Max': '11236',
        'Fwd IAT Min': '11236',
        'Fwd Packets/s': '177.99928',
        'Packet Length Min': '0',
        'Packet Length Max': '0',
        'Packet Length Mean': '0',
        'Packet Length Std': '0',
        'Packet Length Variance': '0',
        'Avg Packet Size': '0',
        'Avg Fwd Segment Size': '0',
        'Subflow Fwd Packets': '2',
        'Subflow Fwd Bytes': '0',
        'Fwd Act Data Packets': '0'
      },
      {
        // 3) Infiltration - Only 30 features
        'Protocol': '6',
        'Flow Duration': '632',
        'Total Fwd Packets': '3',
        'Fwd Packets Length Total': '77',
        'Fwd Packet Length Max': '46',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '25.666666',
        'Fwd Packet Length Std': '23.459185',
        'Flow Bytes/s': '121835.445',
        'Flow Packets/s': '4746.8354',
        'Flow IAT Mean': '316',
        'Flow IAT Std': '429.92093',
        'Flow IAT Max': '620',
        'Flow IAT Min': '12',
        'Fwd IAT Total': '632',
        'Fwd IAT Mean': '316',
        'Fwd IAT Std': '429.92093',
        'Fwd IAT Max': '620',
        'Fwd IAT Min': '12',
        'Fwd Packets/s': '4746.8354',
        'Packet Length Min': '0',
        'Packet Length Max': '46',
        'Packet Length Mean': '30.75',
        'Packet Length Std': '21.68525',
        'Packet Length Variance': '470.25',
        'Avg Packet Size': '41',
        'Avg Fwd Segment Size': '25.666666',
        'Subflow Fwd Packets': '3',
        'Subflow Fwd Bytes': '77',
        'Fwd Act Data Packets': '1'
      },
      {
        // 4) SSH-Bruteforce - Only 30 features
        'Protocol': '6',
        'Flow Duration': '378736',
        'Total Fwd Packets': '22',
        'Fwd Packets Length Total': '1912',
        'Fwd Packet Length Max': '640',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '86.90909',
        'Fwd Packet Length Std': '137.68802',
        'Flow Bytes/s': '12084.936',
        'Flow Packets/s': '116.17591',
        'Flow IAT Mean': '8807.813',
        'Flow IAT Std': '20638.71',
        'Flow IAT Max': '89867',
        'Flow IAT Min': '3',
        'Fwd IAT Total': '378660',
        'Fwd IAT Mean': '18031.428',
        'Fwd IAT Std': '29716.016',
        'Fwd IAT Max': '89867',
        'Fwd IAT Min': '258',
        'Fwd Packets/s': '58.087955',
        'Packet Length Min': '0',
        'Packet Length Max': '976',
        'Packet Length Mean': '101.71111',
        'Packet Length Std': '203.7372',
        'Packet Length Variance': '41508.848',
        'Avg Packet Size': '104.02273',
        'Avg Fwd Segment Size': '86.90909',
        'Subflow Fwd Packets': '22',
        'Subflow Fwd Bytes': '1912',
        'Fwd Act Data Packets': '16'
      },
      {
        // 5) DDoS attacks-LOIC-HTTP - Only 30 features
        'Protocol': '6',
        'Flow Duration': '1195476',
        'Total Fwd Packets': '3',
        'Fwd Packets Length Total': '20',
        'Fwd Packet Length Max': '20',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '6.6666665',
        'Fwd Packet Length Std': '11.547006',
        'Flow Bytes/s': '823.1031',
        'Flow Packets/s': '5.855408',
        'Flow IAT Mean': '199246',
        'Flow IAT Std': '487878.6',
        'Flow IAT Max': '1200000',
        'Flow IAT Min': '2',
        'Fwd IAT Total': '315',
        'Fwd IAT Mean': '157.5',
        'Fwd IAT Std': '219.9102',
        'Fwd IAT Max': '313',
        'Fwd IAT Min': '2',
        'Fwd Packets/s': '2.5094607',
        'Packet Length Min': '0',
        'Packet Length Max': '964',
        'Packet Length Mean': '123',
        'Packet Length Std': '339.8874',
        'Packet Length Variance': '115523.43',
        'Avg Packet Size': '140.57143',
        'Avg Fwd Segment Size': '6.6666665',
        'Subflow Fwd Packets': '3',
        'Subflow Fwd Bytes': '20',
        'Fwd Act Data Packets': '1'
      }
    ];

    const labels = [
      'Benign',
      'DoS',
      'Infiltration',
      'Bruteforce',
      'DDoS'
    ];

    const idx = sampleIndex % samples.length;
    const chosen = samples[idx];
    const nextForm = { ...formData, ...chosen };
    setFormData(nextForm);
    setExpectedLabel(labels[idx]);
    if (featureNames && featureNames.length > 0) {
      const missing = Object.keys(chosen).filter(k => !featureNames.includes(k));
      setUnmatchedKeys(missing);
    }
    setSampleIndex((i) => (i + 1) % samples.length);
  };

  const featureGroups = organizeFeatures();
  const allFeatures = featureNames || Object.values(FEATURE_GROUPS).flat();

  // Show loading state if feature names not loaded
  if (!featureNames || featureNames.length === 0) {
    return (
      <div className="manual-input-container">
        <div className="loading-features">
          <div className="spinner-small"></div>
          <p>Loading feature parameters...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="manual-input-container">
      <div className="input-header">
        <h3>📝 Manual Input - Network Flow Parameters</h3>
        <p>Enter network flow characteristics to classify the traffic ({featureNames.length} parameters)</p>
        {unmatchedKeys.length > 0 && (
          <div className="warning-banner" style={{ marginTop: 8 }}>
            <strong>Note:</strong> {unmatchedKeys.length} preset fields don’t exist in the model’s feature list and were ignored.{' '}
            {unmatchedKeys.slice(0, 10).join(', ')}{unmatchedKeys.length > 10 ? '…' : ''}
          </div>
        )}
        <div className="input-actions">
          <button
            type="button"
            className="btn-sample"
            onClick={handleFillSample}
            disabled={disabled || loading}
            title="Fill sample values (click to cycle through 5 presets)"
          >
            {`Fill Sample (${expectedLabel || 'click to start'})`}
          </button>
          <button
            type="button"
            className="btn-reset"
            onClick={handleReset}
            disabled={disabled || loading}
          >
            Reset All
          </button>
        </div>
        {expectedLabel && (
          <div className="expected-label" style={{ marginTop: 8 }}>
            <strong>Expected Label:</strong> {expectedLabel}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <div className="feature-groups-tabs">
          {Object.keys(featureGroups).map(groupName => (
            <button
              key={groupName}
              type="button"
              className={`group-tab ${activeGroup === groupName ? 'active' : ''}`}
              onClick={() => setActiveGroup(groupName)}
            >
              {groupName}
              <span className="feature-count">
                ({featureGroups[groupName].length})
              </span>
            </button>
          ))}
        </div>

        <div className="features-grid-container">
          {Object.keys(featureGroups).map(groupName => (
            <div
              key={groupName}
              className={`feature-group ${activeGroup === groupName ? 'active' : ''}`}
            >
              <h4 className="group-title">{groupName}</h4>
              <div className="features-grid">
                {featureGroups[groupName].map((feature, index) => (
                  <div key={feature} className="feature-input-wrapper">
                    <label htmlFor={feature} className="feature-label">
                      {feature}
                    </label>
                    <input
                      id={feature}
                      type="number"
                      step="any"
                      className="feature-input"
                      value={formData[feature] || ''}
                      onChange={(e) => handleInputChange(feature, e.target.value)}
                      placeholder="0"
                      disabled={disabled || loading}
                      required
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn-predict"
            disabled={disabled || loading}
          >
            {loading ? (
              <>
                <span className="spinner-small"></span>
                Analyzing...
              </>
            ) : (
              '🔍 Classify Traffic'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ManualInput;

