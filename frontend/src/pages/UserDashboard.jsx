import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const UserDashboard = () => {
  const { user, logout } = useContext(AuthContext);

  if (!user) return null;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Tool Permission Enforcer - User Portal</h1>
        <button onClick={logout} className="logout-btn">Logout</button>
      </header>
      
      <main className="dashboard-main">
        <section className="welcome-section">
          <h2>Good Morning, {user.name.split(' ')[0]}!</h2>
          <div className="user-info-card">
            <p><strong>Role:</strong> {user.role}</p>
            <p><strong>Agent:</strong> {user.agent?.name || 'Loading agent...'}</p>
          </div>
        </section>

        <section className="navigation-cards">
          <div className="card">
            <h3>Dashboard</h3>
            <p>Overview of your activity</p>
          </div>
          <div className="card">
            <h3>Customers</h3>
            <p>Manage CRM customers</p>
          </div>
          <div className="card">
            <h3>AI Assistant</h3>
            <p>Interact with your Agent</p>
          </div>
          <div className="card">
            <h3>My Activity</h3>
            <p>View your past actions</p>
          </div>
          <div className="card">
            <h3>Settings</h3>
            <p>Manage your account</p>
          </div>
        </section>
      </main>
    </div>
  );
};

export default UserDashboard;
