import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import RegionExplorer from './pages/RegionExplorer';
import PeakTraffic from './pages/PeakTraffic';
import RiskPrediction from './pages/RiskPrediction';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/explorer" element={<RegionExplorer />} />
            <Route path="/peak" element={<PeakTraffic />} />
            <Route path="/predict" element={<RiskPrediction />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
