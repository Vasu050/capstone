import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, MapPin } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE;

const PeakTraffic = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/usage/peak`)
      .then(res => {
        setData(res.data);
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
        <h1 className="page-title">Peak Traffic Analysis</h1>
        <p className="page-subtitle">Identifying critical load points across the network</p>
      </header>

      <div className="kpi-grid">
        <div className="card" style={{ flex: 1 }}>
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingUp color="var(--primary)" /> Top 5 High-Traffic Hours
          </h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Hour</th>
                  <th>Total Usage (MB)</th>
                </tr>
              </thead>
              <tbody>
                {data?.top_hours.map((h) => (
                  <tr key={h.hour}>
                    <td>{h.hour}:00</td>
                    <td style={{ fontWeight: 600 }}>{h.total_usage.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card" style={{ flex: 1 }}>
          <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <MapPin color="var(--primary)" /> Top 5 Busiest Regions
          </h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Region</th>
                  <th>Total Usage (MB)</th>
                </tr>
              </thead>
              <tbody>
                {data?.top_regions.map((r) => (
                  <tr key={r.region}>
                    <td>{r.region}</td>
                    <td style={{ fontWeight: 600 }}>{r.total_usage.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PeakTraffic;
