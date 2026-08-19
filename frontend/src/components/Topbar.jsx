import React, { useContext } from 'react';
import { useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Topbar = ({ toggleSidebar }) => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();
  
  // Format page title from pathname
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
    if (path === '/reports') return 'Reports';
    if (path === '/settings') return 'Settings';
    return 'CRM Portal';
  };

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="menu-toggle" onClick={toggleSidebar}>
          ☰
        </button>
        <h2 className="page-title">{getPageTitle()}</h2>
      </div>
      
      <div className="topbar-right">
        <div className="notification-bell">
          🔔
        </div>
        {user && (
          <div style={{display: 'flex', alignItems: 'center', gap: '15px'}}>
            <div style={{textAlign: 'right'}}>
              <div style={{fontWeight: 500, fontSize: '0.9rem'}}>{user.name}</div>
              <div style={{fontSize: '0.75rem', color: 'var(--text-muted)'}} className={`badge ${user.role === 'ADMIN' ? 'danger' : 'info'}`}>
                {user.role}
              </div>
            </div>
            <button className="logout-btn" onClick={logout}>Logout</button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Topbar;
