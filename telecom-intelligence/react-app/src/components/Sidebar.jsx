import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Map, BarChart3, ShieldAlert } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Region Explorer', path: '/explorer', icon: <Map size={20} /> },
    { name: 'Peak Traffic', path: '/peak', icon: <BarChart3 size={20} /> },
    { name: 'Risk Prediction', path: '/predict', icon: <ShieldAlert size={20} /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        Telecom Intel
      </div>
      <nav className="nav-links">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            {item.icon}
            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
