import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Sidebar = ({ isOpen }) => {
  const { user } = useContext(AuthContext);

  if (!user) return null;

  const isAdmin = user.role === 'ADMIN';

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <div>
          <h2>CRM Portal</h2>
          <p>AI-Powered CRM</p>
        </div>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className="nav-item">Home</NavLink>
        <NavLink to="/customers" className="nav-item">Customers</NavLink>
        <NavLink to="/ai-assistant" className="nav-item">AI Assistant</NavLink>
        
        {isAdmin && (
          <>
            <NavLink to="/signup-requests" className="nav-item">Signup Requests</NavLink>
            <NavLink to="/users" className="nav-item">Users</NavLink>
            <NavLink to="/agents" className="nav-item">Agents</NavLink>
            <NavLink to="/audit-logs" className="nav-item">Audit Logs</NavLink>
            <NavLink to="/security-alerts" className="nav-item">Security Alerts</NavLink>
          </>
        )}
        
        <NavLink to="/reports" className="nav-item">Reports</NavLink>
        <NavLink to="/settings" className="nav-item">Settings</NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="avatar">
          {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
        </div>
        <div className="user-info">
          <span className="user-name">{user.name}</span>
          <span className="user-role">{user.role}</span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
