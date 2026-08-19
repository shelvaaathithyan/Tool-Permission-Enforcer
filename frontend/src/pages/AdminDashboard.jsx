import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const AdminDashboard = () => {
  const { user, logout } = useContext(AuthContext);

  if (!user) return null;

  return (
    <div className="dashboard-container admin-theme">
      <header className="dashboard-header">
        <h1>Tool Permission Enforcer - Admin Portal</h1>
        <button onClick={logout} className="logout-btn">Logout</button>
      </header>
      
      <main className="dashboard-main">
        <section className="welcome-section">
          <h2>Admin Dashboard</h2>
          <div className="user-info-card">
            <p><strong>Administrator:</strong> {user.name}</p>
            <p><strong>Agent:</strong> {user.agent?.name || 'Loading agent...'}</p>
          </div>
        </section>

        <section className="navigation-cards">
          <div className="card">
            <h3>Dashboard</h3>
            <p>System overview</p>
          </div>
          <div className="card">
            <h3>Users & Agents</h3>
            <p>Manage platform identities</p>
          </div>
          <div className="card">
            <h3>Customers</h3>
            <p>View CRM data</p>
          </div>
          <div className="card">
            <h3>Audit Logs</h3>
            <p>System-wide activity logs</p>
          </div>
          <div className="card">
            <h3>Security Alerts</h3>
            <p>Review policy violations</p>
          </div>
          <div className="card">
            <h3>Policies</h3>
            <p>Manage agent permissions</p>
          </div>
          <div className="card">
            <h3>Reports</h3>
            <p>System reports</p>
          </div>
          <div className="card">
            <h3>My AI Assistant</h3>
            <p>Interact with Admin Agent</p>
          </div>
        </section>
      </main>
    </div>
  );
};

export default AdminDashboard;
