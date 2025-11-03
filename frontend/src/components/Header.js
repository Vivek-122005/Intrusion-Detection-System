import React from 'react';
import '../styles/Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo-icon">🛡️</div>
          <div className="logo-text">
            <h1>Intrusion Detection System</h1>
            <p>ML-Based Network Security Analysis</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

