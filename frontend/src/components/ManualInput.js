import React, { useState, useEffect } from 'react';
import '../styles/ManualInput.css';

// Feature groups for better organization
const FEATURE_GROUPS = {
  'Basic Flow Information': [
    'Protocol',
    'Flow Duration',
    'Total Fwd Packets',
    'Total Backward Packets',
  ],
  'Forward Packets': [
    'Fwd Packets Length Total',
    'Fwd Packet Length Max',
    'Fwd Packet Length Min',
    'Fwd Packet Length Mean',
    'Fwd Packet Length Std',
    'Fwd Packets/s',
    'Fwd Header Length',
    'Fwd IAT Total',
    'Fwd IAT Mean',
    'Fwd IAT Std',
    'Fwd IAT Max',
    'Fwd IAT Min',
    'Fwd PSH Flags',
    'Fwd URG Flags',
    'Fwd Act Data Packets',
    'Fwd Seg Size Min',
    'Fwd Avg Bytes/Bulk',
    'Fwd Avg Packets/Bulk',
    'Fwd Avg Bulk Rate',
    'Avg Fwd Segment Size',
    'Subflow Fwd Packets',
    'Subflow Fwd Bytes',
    'Init Fwd Win Bytes',
  ],
  'Backward Packets': [
    'Bwd Packets Length Total',
    'Bwd Packet Length Max',
    'Bwd Packet Length Min',
    'Bwd Packet Length Mean',
    'Bwd Packet Length Std',
    'Bwd Packets/s',
    'Bwd Header Length',
    'Bwd IAT Total',
    'Bwd IAT Mean',
    'Bwd IAT Std',
    'Bwd IAT Max',
    'Bwd IAT Min',
    'Bwd PSH Flags',
    'Bwd URG Flags',
    'Bwd Avg Bytes/Bulk',
    'Bwd Avg Packets/Bulk',
    'Bwd Avg Bulk Rate',
    'Avg Bwd Segment Size',
    'Subflow Bwd Packets',
    'Subflow Bwd Bytes',
    'Init Bwd Win Bytes',
  ],
  'Flow Statistics': [
    'Flow Bytes/s',
    'Flow Packets/s',
    'Flow IAT Mean',
    'Flow IAT Std',
    'Flow IAT Max',
    'Flow IAT Min',
    'Down/Up Ratio',
  ],
  'Packet Statistics': [
    'Packet Length Min',
    'Packet Length Max',
    'Packet Length Mean',
    'Packet Length Std',
    'Packet Length Variance',
    'Avg Packet Size',
  ],
  'TCP Flags': [
    'FIN Flag Count',
    'SYN Flag Count',
    'RST Flag Count',
    'PSH Flag Count',
    'ACK Flag Count',
    'URG Flag Count',
    'CWE Flag Count',
    'ECE Flag Count',
  ],
  'Timing Statistics': [
    'Active Mean',
    'Active Std',
    'Active Max',
    'Active Min',
    'Idle Mean',
    'Idle Std',
    'Idle Max',
    'Idle Min',
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
    // Five cycling samples based on provided rows (no Label field)
    const samples = [
      {
        // 1) Benign
        'Protocol': '6',
        'Flow Duration': '1832',
        'Total Fwd Packets': '5',
        'Total Backward Packets': '2',
        'Fwd Packets Length Total': '935',
        'Bwd Packets Length Total': '299',
        'Fwd Packet Length Max': '935',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '187',
        'Fwd Packet Length Std': '418.1447',
        'Bwd Packet Length Max': '299',
        'Bwd Packet Length Min': '0',
        'Bwd Packet Length Mean': '149.5',
        'Bwd Packet Length Std': '211.42493',
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
        'Bwd IAT Total': '935',
        'Bwd IAT Mean': '935',
        'Bwd IAT Std': '0',
        'Bwd IAT Max': '935',
        'Bwd IAT Min': '935',
        'Fwd PSH Flags': '0',
        'Bwd PSH Flags': '0',
        'Fwd URG Flags': '0',
        'Bwd URG Flags': '0',
        'Fwd Header Length': '124',
        'Bwd Header Length': '40',
        'Fwd Packets/s': '2729.2576',
        'Bwd Packets/s': '1091.703',
        'Packet Length Min': '0',
        'Packet Length Max': '935',
        'Packet Length Mean': '154.25',
        'Packet Length Std': '332.36844',
        'Packet Length Variance': '110468.79',
        'FIN Flag Count': '0',
        'SYN Flag Count': '0',
        'RST Flag Count': '1',
        'PSH Flag Count': '1',
        'ACK Flag Count': '0',
        'URG Flag Count': '0',
        'CWE Flag Count': '0',
        'ECE Flag Count': '1',
        'Down/Up Ratio': '0',
        'Avg Packet Size': '176.28572',
        'Avg Fwd Segment Size': '187',
        'Avg Bwd Segment Size': '149.5',
        'Fwd Avg Bytes/Bulk': '0',
        'Fwd Avg Packets/Bulk': '0',
        'Fwd Avg Bulk Rate': '0',
        'Bwd Avg Bytes/Bulk': '0',
        'Bwd Avg Packets/Bulk': '0',
        'Bwd Avg Bulk Rate': '0',
        'Subflow Fwd Packets': '5',
        'Subflow Fwd Bytes': '935',
        'Subflow Bwd Packets': '2',
        'Subflow Bwd Bytes': '299',
        'Init Fwd Win Bytes': '65535',
        'Init Bwd Win Bytes': '32768',
        'Fwd Act Data Packets': '1',
        'Fwd Seg Size Min': '20',
        'Active Mean': '0',
        'Active Std': '0',
        'Active Max': '0',
        'Active Min': '0',
        'Idle Mean': '0',
        'Idle Std': '0',
        'Idle Max': '0',
        'Idle Min': '0'
      },
      {
        // 2) DoS attacks-Hulk
        'Protocol': '6',
        'Flow Duration': '11236',
        'Total Fwd Packets': '2',
        'Total Backward Packets': '0',
        'Fwd Packets Length Total': '0',
        'Bwd Packets Length Total': '0',
        'Fwd Packet Length Max': '0',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '0',
        'Fwd Packet Length Std': '0',
        'Bwd Packet Length Max': '0',
        'Bwd Packet Length Min': '0',
        'Bwd Packet Length Mean': '0',
        'Bwd Packet Length Std': '0',
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
        'Bwd IAT Total': '0',
        'Bwd IAT Mean': '0',
        'Bwd IAT Std': '0',
        'Bwd IAT Max': '0',
        'Bwd IAT Min': '0',
        'Fwd PSH Flags': '0',
        'Bwd PSH Flags': '0',
        'Fwd URG Flags': '0',
        'Bwd URG Flags': '0',
        'Fwd Header Length': '64',
        'Bwd Header Length': '0',
        'Fwd Packets/s': '177.99928',
        'Bwd Packets/s': '0',
        'Packet Length Min': '0',
        'Packet Length Max': '0',
        'Packet Length Mean': '0',
        'Packet Length Std': '0',
        'Packet Length Variance': '0',
        'FIN Flag Count': '0',
        'SYN Flag Count': '0',
        'RST Flag Count': '0',
        'PSH Flag Count': '0',
        'ACK Flag Count': '0',
        'URG Flag Count': '0',
        'CWE Flag Count': '1',
        'ECE Flag Count': '0',
        'Down/Up Ratio': '0',
        'Avg Packet Size': '0',
        'Avg Fwd Segment Size': '0',
        'Avg Bwd Segment Size': '0',
        'Fwd Avg Bytes/Bulk': '0',
        'Fwd Avg Packets/Bulk': '0',
        'Fwd Avg Bulk Rate': '0',
        'Bwd Avg Bytes/Bulk': '0',
        'Bwd Avg Packets/Bulk': '0',
        'Bwd Avg Bulk Rate': '0',
        'Subflow Fwd Packets': '2',
        'Subflow Fwd Bytes': '0',
        'Subflow Bwd Packets': '0',
        'Subflow Bwd Bytes': '0',
        'Init Fwd Win Bytes': '225',
        'Init Bwd Win Bytes': '-1',
        'Fwd Act Data Packets': '0',
        'Fwd Seg Size Min': '32',
        'Active Mean': '0',
        'Active Std': '0',
        'Active Max': '0',
        'Active Min': '0',
        'Idle Mean': '0',
        'Idle Std': '0',
        'Idle Max': '0',
        'Idle Min': '0'
      },
      {
        // 3) Infilteration
        'Protocol': '6',
        'Flow Duration': '632',
        'Total Fwd Packets': '3',
        'Total Backward Packets': '0',
        'Fwd Packets Length Total': '77',
        'Bwd Packets Length Total': '0',
        'Fwd Packet Length Max': '46',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '25.666666',
        'Fwd Packet Length Std': '23.459185',
        'Bwd Packet Length Max': '0',
        'Bwd Packet Length Min': '0',
        'Bwd Packet Length Mean': '0',
        'Bwd Packet Length Std': '0',
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
        'Bwd IAT Total': '0',
        'Bwd IAT Mean': '0',
        'Bwd IAT Std': '0',
        'Bwd IAT Max': '0',
        'Bwd IAT Min': '0',
        'Fwd PSH Flags': '1',
        'Bwd PSH Flags': '0',
        'Fwd URG Flags': '0',
        'Bwd URG Flags': '0',
        'Fwd Header Length': '60',
        'Bwd Header Length': '0',
        'Fwd Packets/s': '4746.8354',
        'Bwd Packets/s': '0',
        'Packet Length Min': '0',
        'Packet Length Max': '46',
        'Packet Length Mean': '30.75',
        'Packet Length Std': '21.68525',
        'Packet Length Variance': '470.25',
        'FIN Flag Count': '0',
        'SYN Flag Count': '1',
        'RST Flag Count': '0',
        'PSH Flag Count': '0',
        'ACK Flag Count': '1',
        'URG Flag Count': '0',
        'CWE Flag Count': '0',
        'ECE Flag Count': '0',
        'Down/Up Ratio': '0',
        'Avg Packet Size': '41',
        'Avg Fwd Segment Size': '25.666666',
        'Avg Bwd Segment Size': '0',
        'Fwd Avg Bytes/Bulk': '0',
        'Fwd Avg Packets/Bulk': '0',
        'Fwd Avg Bulk Rate': '0',
        'Bwd Avg Bytes/Bulk': '0',
        'Bwd Avg Packets/Bulk': '0',
        'Bwd Avg Bulk Rate': '0',
        'Subflow Fwd Packets': '3',
        'Subflow Fwd Bytes': '77',
        'Subflow Bwd Packets': '0',
        'Subflow Bwd Bytes': '0',
        'Init Fwd Win Bytes': '256',
        'Init Bwd Win Bytes': '-1',
        'Fwd Act Data Packets': '1',
        'Fwd Seg Size Min': '20',
        'Active Mean': '0',
        'Active Std': '0',
        'Active Max': '0',
        'Active Min': '0',
        'Idle Mean': '0',
        'Idle Std': '0',
        'Idle Max': '0',
        'Idle Min': '0'
      },
      {
        // 4) SSH-Bruteforce
        'Protocol': '6',
        'Flow Duration': '378736',
        'Total Fwd Packets': '22',
        'Total Backward Packets': '22',
        'Fwd Packets Length Total': '1912',
        'Bwd Packets Length Total': '2665',
        'Fwd Packet Length Max': '640',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '86.90909',
        'Fwd Packet Length Std': '137.68802',
        'Bwd Packet Length Max': '976',
        'Bwd Packet Length Min': '0',
        'Bwd Packet Length Mean': '121.13636',
        'Bwd Packet Length Std': '258.64157',
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
        'Bwd IAT Total': '378733',
        'Bwd IAT Mean': '18034.904',
        'Bwd IAT Std': '36022.074',
        'Bwd IAT Max': '129772',
        'Bwd IAT Min': '8',
        'Fwd PSH Flags': '0',
        'Bwd PSH Flags': '0',
        'Fwd URG Flags': '0',
        'Bwd URG Flags': '0',
        'Fwd Header Length': '712',
        'Bwd Header Length': '712',
        'Fwd Packets/s': '58.087955',
        'Bwd Packets/s': '58.087955',
        'Packet Length Min': '0',
        'Packet Length Max': '976',
        'Packet Length Mean': '101.71111',
        'Packet Length Std': '203.7372',
        'Packet Length Variance': '41508.848',
        'FIN Flag Count': '0',
        'SYN Flag Count': '0',
        'RST Flag Count': '0',
        'PSH Flag Count': '1',
        'ACK Flag Count': '0',
        'URG Flag Count': '0',
        'CWE Flag Count': '0',
        'ECE Flag Count': '0',
        'Down/Up Ratio': '1',
        'Avg Packet Size': '104.02273',
        'Avg Fwd Segment Size': '86.90909',
        'Avg Bwd Segment Size': '121.13636',
        'Fwd Avg Bytes/Bulk': '0',
        'Fwd Avg Packets/Bulk': '0',
        'Fwd Avg Bulk Rate': '0',
        'Bwd Avg Bytes/Bulk': '0',
        'Bwd Avg Packets/Bulk': '0',
        'Bwd Avg Bulk Rate': '0',
        'Subflow Fwd Packets': '22',
        'Subflow Fwd Bytes': '1912',
        'Subflow Bwd Packets': '22',
        'Subflow Bwd Bytes': '2665',
        'Init Fwd Win Bytes': '26883',
        'Init Bwd Win Bytes': '230',
        'Fwd Act Data Packets': '16',
        'Fwd Seg Size Min': '32',
        'Active Mean': '0',
        'Active Std': '0',
        'Active Max': '0',
        'Active Min': '0',
        'Idle Mean': '0',
        'Idle Std': '0',
        'Idle Max': '0',
        'Idle Min': '0'
      },
      {
        // 5) DDoS attacks-LOIC-HTTP
        'Protocol': '6',
        'Flow Duration': '1195476',
        'Total Fwd Packets': '3',
        'Total Backward Packets': '4',
        'Fwd Packets Length Total': '20',
        'Bwd Packets Length Total': '964',
        'Fwd Packet Length Max': '20',
        'Fwd Packet Length Min': '0',
        'Fwd Packet Length Mean': '6.6666665',
        'Fwd Packet Length Std': '11.547006',
        'Bwd Packet Length Max': '964',
        'Bwd Packet Length Min': '0',
        'Bwd Packet Length Mean': '241',
        'Bwd Packet Length Std': '482',
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
        'Bwd IAT Total': '1200000',
        'Bwd IAT Mean': '398490',
        'Bwd IAT Std': '689905.3',
        'Bwd IAT Max': '1200000',
        'Bwd IAT Min': '31',
        'Fwd PSH Flags': '0',
        'Bwd PSH Flags': '0',
        'Fwd URG Flags': '0',
        'Bwd URG Flags': '0',
        'Fwd Header Length': '72',
        'Bwd Header Length': '92',
        'Fwd Packets/s': '2.5094607',
        'Bwd Packets/s': '3.3459475',
        'Packet Length Min': '0',
        'Packet Length Max': '964',
        'Packet Length Mean': '123',
        'Packet Length Std': '339.8874',
        'Packet Length Variance': '115523.43',
        'FIN Flag Count': '0',
        'SYN Flag Count': '0',
        'RST Flag Count': '1',
        'PSH Flag Count': '1',
        'ACK Flag Count': '0',
        'URG Flag Count': '0',
        'CWE Flag Count': '0',
        'ECE Flag Count': '1',
        'Down/Up Ratio': '1',
        'Avg Packet Size': '140.57143',
        'Avg Fwd Segment Size': '6.6666665',
        'Avg Bwd Segment Size': '241',
        'Fwd Avg Bytes/Bulk': '0',
        'Fwd Avg Packets/Bulk': '0',
        'Fwd Avg Bulk Rate': '0',
        'Bwd Avg Bytes/Bulk': '0',
        'Bwd Avg Packets/Bulk': '0',
        'Bwd Avg Bulk Rate': '0',
        'Subflow Fwd Packets': '3',
        'Subflow Fwd Bytes': '20',
        'Subflow Bwd Packets': '4',
        'Subflow Bwd Bytes': '964',
        'Init Fwd Win Bytes': '8192',
        'Init Bwd Win Bytes': '211',
        'Fwd Act Data Packets': '1',
        'Fwd Seg Size Min': '20',
        'Active Mean': '0',
        'Active Std': '0',
        'Active Max': '0',
        'Active Min': '0',
        'Idle Mean': '0',
        'Idle Std': '0',
        'Idle Max': '0',
        'Idle Min': '0'
      }
    ];

    const labels = [
      'Benign',
      'DoS attacks-Hulk',
      'Infilteration',
      'SSH-Bruteforce',
      'DDoS attacks-LOIC-HTTP'
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

