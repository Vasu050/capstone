import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Phone, MessageSquare, Globe, Clock, MapPin } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE;

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/usage/summary`)
      .then(res => {
        setSummary(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="main-content">Loading...</div>;

  return (
    <div className="main-content fade-in">
      <header className="page-header">
        <h1 className="page-title">Network Usage Summary</h1>
        <p className="page-subtitle">Real-time KPIs from the Telecom Data Warehouse</p>
      </header>

      <div className="kpi-grid">
        <div className="card">
          <div className="kpi-label">Total Calls</div>
          <div className="kpi-value">{summary?.total_calls.toLocaleString()}</div>
          <div className="kpi-trend success"><Phone size={16} /> Volume Stable</div>
        </div>
        <div className="card">
          <div className="kpi-label">Total SMS</div>
          <div className="kpi-value">{summary?.total_sms.toLocaleString()}</div>
          <div className="kpi-trend success"><MessageSquare size={16} /> Growth +2%</div>
        </div>
        <div className="card">
          <div className="kpi-label">Internet Usage (MB)</div>
          <div className="kpi-value">{summary?.total_internet_mb.toLocaleString()}</div>
          <div className="kpi-trend warning"><Globe size={16} /> High Traffic</div>
        </div>
      </div>

      <div className="kpi-grid">
        <div className="card">
          <div className="kpi-label">Peak Hour</div>
          <div className="kpi-value"><Clock size={24} style={{marginRight: '10px'}}/> {summary?.peak_hour}:00</div>
          <p style={{color: 'var(--text-muted)'}}>Daily System Peak</p>
        </div>
        <div className="card">
          <div className="kpi-label">Busiest Region</div>
          <div className="kpi-value"><MapPin size={24} style={{marginRight: '10px'}}/> {summary?.busiest_region}</div>
          <p style={{color: 'var(--text-muted)'}}>Max Traffic Load</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
