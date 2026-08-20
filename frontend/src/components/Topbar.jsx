import React, { useContext } from 'react';
import { useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Topbar = ({ toggleSidebar }) => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();
  
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'Dashboard';
    if (path === '/customers') return 'Customers';
    if (path === '/ai-assistant') return 'AI Assistant';
    if (path === '/signup-requests') return 'Signup Requests';
    if (path === '/users') return 'Users';
    if (path === '/agents') return 'Agents';
    if (path === '/audit-logs') return 'Audit Logs';
    if (path === '/security-alerts') return 'Security Alerts';
    if (path === '/settings') return 'Settings';
    return 'CRM Portal';
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="menu-toggle" onClick={toggleSidebar} aria-label="Toggle navigation">
          ☰
        </button>
        <h2 className="page-title">{getPageTitle()}</h2>
      </div>
      
      <div className="topbar-right">
        {user && (
          <div className="topbar-user" style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div className="topbar-user-name" style={{ fontSize: '14px', fontWeight: 600 }}>{user.name}</div>
              <span className={`badge ${user.role === 'ADMIN' ? 'danger' : user.role === 'MANAGER' ? 'warning' : 'info'}`} style={{ fontSize: '10px', marginTop: '2px' }}>
                {user.role}
              </span>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={logout}>Logout</button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Topbar;
