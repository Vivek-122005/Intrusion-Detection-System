import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import '../styles/ResultsDisplay.css';

const COLORS = ['#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#ec4899', '#14b8a6'];

const ResultsDisplay = ({ results }) => {
  const { statistics, prediction_counts, classes, total_samples } = results;

  // Prepare data for charts
  const pieData = Object.entries(prediction_counts).map(([name, value]) => ({
    name,
    value: parseInt(value)
  }));

  const barData = pieData.sort((a, b) => b.value - a.value);

  const getColorForCategory = (name) => {
    if (name === 'Benign') return COLORS[0];
    return COLORS[1 + (name.length % (COLORS.length - 1))];
  };

  return (
    <div className="results-display">
      <div className="results-header">
        <h2>Detection Results</h2>
        <div className="summary-badges">
          <div className="badge total">
            <span className="badge-label">Total Samples</span>
            <span className="badge-value">{total_samples.toLocaleString()}</span>
          </div>
          <div className="badge benign">
            <span className="badge-label">Benign</span>
            <span className="badge-value">{statistics.benign_count.toLocaleString()}</span>
          </div>
          <div className="badge attack">
            <span className="badge-label">Attacks</span>
            <span className="badge-value">{statistics.attack_count.toLocaleString()}</span>
          </div>
          <div className="badge percentage">
            <span className="badge-label">Threat Level</span>
            <span className="badge-value">{statistics.attack_percentage.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      <div className="charts-container">
        <div className="chart-card">
          <h3>Distribution by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getColorForCategory(entry.name)} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Attack Types Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45} 
                textAnchor="end" 
                height={100}
                tick={{ fontSize: 12 }}
              />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="detailed-results">
        <h3>Detailed Breakdown</h3>
        <div className="results-table">
          <div className="table-header">
            <span>Attack Category</span>
            <span>Count</span>
            <span>Percentage</span>
          </div>
          {barData.map((item, index) => (
            <div key={index} className="table-row">
              <span className="category-name">{item.name}</span>
              <span className="category-count">{item.value.toLocaleString()}</span>
              <span className="category-percentage">
                {((item.value / total_samples) * 100).toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {statistics.accuracy !== null && (
        <div></div>
      )}
    </div>
  );
};

export default ResultsDisplay;

