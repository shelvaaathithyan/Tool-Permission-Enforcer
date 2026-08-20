import React, { useContext } from 'react';
import { NavLink } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Users, 
  Bot, 
  ClipboardList, 
  UserCog, 
  Cpu, 
  FileClock, 
  ShieldAlert, 
  Settings 
} from 'lucide-react';

const Sidebar = ({ isOpen }) => {
  const { user } = useContext(AuthContext);

  if (!user) return null;

  const isAdmin = user.role === 'ADMIN';

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header" style={{ justifyContent: 'center', textAlign: 'center' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>CRM Portal</h2>
          <p style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.5)', letterSpacing: '0.8px' }}>AI-Powered CRM</p>
        </div>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className="nav-item">
          <LayoutDashboard className="nav-icon" size={18} /> Dashboard
        </NavLink>
        <NavLink to="/customers" className="nav-item">
          <Users className="nav-icon" size={18} /> Customers
        </NavLink>
        <NavLink to="/ai-assistant" className="nav-item">
          <Bot className="nav-icon" size={18} /> AI Assistant
        </NavLink>
        
        {isAdmin && (
          <>
            <span className="nav-section-label">Administration</span>
            <NavLink to="/signup-requests" className="nav-item">
              <ClipboardList className="nav-icon" size={18} /> Signup Requests
            </NavLink>
            <NavLink to="/users" className="nav-item">
              <UserCog className="nav-icon" size={18} /> Users
            </NavLink>
            <NavLink to="/agents" className="nav-item">
              <Cpu className="nav-icon" size={18} /> Agents
            </NavLink>
            <NavLink to="/audit-logs" className="nav-item">
              <FileClock className="nav-icon" size={18} /> Audit Logs
            </NavLink>
            <NavLink to="/security-alerts" className="nav-item">
              <ShieldAlert className="nav-icon" size={18} /> Security Alerts
            </NavLink>
          </>
        )}

        <span className="nav-section-label">Account</span>
        <NavLink to="/settings" className="nav-item">
          <Settings className="nav-icon" size={18} /> Settings
        </NavLink>
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
