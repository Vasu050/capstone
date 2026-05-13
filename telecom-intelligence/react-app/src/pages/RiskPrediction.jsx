import React, { useState } from 'react';
import axios from 'axios';
import { ShieldAlert, AlertTriangle, CheckCircle } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE;

const RiskPrediction = () => {
  const [formData, setFormData] = useState({
    region: 'Centro',
    avg_usage: 1240.5,
    growth_rate: 0.12,
    variability: 0.34
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    axios.post(`${API_BASE}/predict-usage-risk`, formData)
      .then(res => {
        setResult(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'region' ? value : parseFloat(value) || 0
    }));
  };

  return (
    <div className="main-content fade-in">
      <header className="page-header">
        <h1 className="page-title">Network Risk Prediction</h1>
        <p className="page-subtitle">Predict congestion risk and anomalies using ML parameters</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2.5rem' }}>
        <div className="form-card">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Region Name</label>
              <input name="region" className="form-input" value={formData.region} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Average Usage (MB)</label>
              <input name="avg_usage" type="number" step="0.1" className="form-input" value={formData.avg_usage} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Growth Rate (0.0 - 1.0)</label>
              <input name="growth_rate" type="number" step="0.01" className="form-input" value={formData.growth_rate} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Usage Variability</label>
              <input name="variability" type="number" step="0.01" className="form-input" value={formData.variability} onChange={handleChange} />
            </div>
            <button type="submit" className="btn" disabled={loading}>
              {loading ? 'Analyzing...' : 'Run Prediction'}
            </button>
          </form>
        </div>

        <div>
          {result && (
            <div className={`card fade-in result-card ${result.congestion_risk.toLowerCase()}`}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                {result.congestion_risk === 'HIGH' ? <ShieldAlert size={48} color="var(--danger)" /> : 
                 result.congestion_risk === 'MEDIUM' ? <AlertTriangle size={48} color="var(--warning)" /> : 
                 <CheckCircle size={48} color="var(--success)" />}
                <div>
                  <h2 style={{ fontSize: '1.5rem' }}>Congestion Risk: {result.congestion_risk}</h2>
                  <div className={`risk-label risk-${result.congestion_risk.toLowerCase()}`}>
                    Score: {(result.score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '0.75rem' }}>
                <p style={{ color: 'var(--text-muted)' }}>Anomaly Detection:</p>
                <p style={{ fontWeight: 600 }}>{result.anomaly_flag ? '⚠ Anomaly Detected' : '✓ Normal Behavior'}</p>
              </div>

              <p style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                The prediction is based on the average usage of {formData.avg_usage} MB and a growth rate of {(formData.growth_rate * 100).toFixed(0)}%.
              </p>
            </div>
          )}
          {!result && !loading && (
            <div className="card" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-muted)' }}>Enter parameters and run prediction to see results.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RiskPrediction;
