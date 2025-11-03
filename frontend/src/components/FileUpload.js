import React, { useRef, useState } from 'react';
import '../styles/FileUpload.css';

const FileUpload = ({ onFileUpload, loading, disabled }) => {
  const fileInputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    const validExtensions = ['.csv', '.parquet'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!validExtensions.includes(fileExtension)) {
      alert('Please upload a CSV or Parquet file');
      return;
    }
    
    onFileUpload(file);
  };

  return (
    <div className="file-upload-container">
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${disabled ? 'disabled' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.parquet"
          onChange={handleFileInput}
          disabled={disabled || loading}
          style={{ display: 'none' }}
        />
        
        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <h3>Upload Network Traffic Data</h3>
          <p>Drag and drop your file here, or click to browse</p>
          <p className="file-types">Supports: CSV, Parquet</p>
          <button
            className="upload-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || loading}
          >
            {loading ? 'Processing...' : 'Choose File'}
          </button>
        </div>
      </div>
      
      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Analyzing network traffic...</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;

