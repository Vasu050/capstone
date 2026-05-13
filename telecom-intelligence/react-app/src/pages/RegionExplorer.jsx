import React, { useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Search } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE;

const RegionExplorer = () => {
  const [region, setRegion] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRegionData = () => {
    if (!region) return;
    setLoading(true);
    setError(null);
    axios.get(`${API_BASE}/usage/region/${region}`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.detail || 'Error fetching data');
        setLoading(false);
      });
  };

  return (
    <div className="main-content fade-in">
      <header className="page-header">
        <h1 className="page-title">Region Explorer</h1>
        <p className="page-subtitle">Analyze hourly traffic patterns for specific grid regions</p>
      </header>

      <div className="form-group" style={{ display: 'flex', gap: '1rem', maxWidth: '600px' }}>
        <input
          type="text"
          className="form-input"
          placeholder="Enter region name (e.g. Centro, Nord)"
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && fetchRegionData()}
        />
        <button className="btn" onClick={fetchRegionData} style={{ width: 'auto' }}>
          <Search size={20} />
        </button>
      </div>

      {loading && <p>Searching...</p>}
      {error && <p style={{ color: 'var(--danger)' }}>{error}</p>}

      {data && (
        <div className="fade-in">
          <div className="chart-container">
            <h3>Hourly Internet Usage (MB)</h3>
            <div style={{ height: '300px', marginTop: '1.5rem' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.hourly_distribution}>
                  <defs>
                    <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="hour" stroke="var(--text-muted)" />
                  <YAxis stroke="var(--text-muted)" />
                  <Tooltip 
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
                    itemStyle={{ color: 'white' }}
                  />
                  <Area type="monotone" dataKey="internet_mb" stroke="var(--primary)" fillOpacity={1} fill="url(#colorUsage)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="kpi-grid">
            <div className="card">
              <h3>Calls vs SMS Distribution</h3>
              <div style={{ height: '250px', marginTop: '1.5rem' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.hourly_distribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="hour" stroke="var(--text-muted)" />
                    <YAxis stroke="var(--text-muted)" />
                    <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }} />
                    <Bar dataKey="calls" fill="#818cf8" />
                    <Bar dataKey="sms" fill="#c084fc" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RegionExplorer;
