import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import PageLoader from '../components/PageLoader';
import ErrorState from '../components/ErrorState';

const UserDashboard = () => {
  const { token, user } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/my-stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      } else {
        setError('Failed to load dashboard data.');
      }
    } catch (e) {
      console.error(e);
      setError('A network error occurred.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [token]);

  if (loading && !stats) {
    return <PageLoader message="Loading dashboard..." delay={250} />;
  }

  if (error && !stats) {
    return <ErrorState message={error} onRetry={fetchStats} />;
  }

  return (
    <div style={{ position: 'relative', minHeight: '300px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: 0 }}>
          {user?.name ? `Welcome, ${user.name}` : 'Welcome'}
        </h2>
        <p style={{ color: 'var(--text-muted)', margin: '5px 0 0 0', fontSize: '14px' }}>Here's an overview of your CRM and Agent activity.</p>
      </div>

      <div className="card-row">
        <div className="stat-card">
          <span className="stat-title">Total Customers</span>
          <span className="stat-value">{stats?.total_customers || 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">My Active Sessions</span>
          <span className="stat-value">{stats?.active_sessions || 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Allowed Operations</span>
          <span className="stat-value" style={{ color: 'var(--success-color)' }}>{stats?.allowed_operations || 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Blocked Operations</span>
          <span className="stat-value" style={{ color: 'var(--danger-color)' }}>{stats?.blocked_operations || 0}</span>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <h3>My Agent Status</h3>
          </div>
          <div style={{ marginBottom: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Agent Name</span>
              <span style={{ fontWeight: '600', fontSize: '14px' }}>{user?.agent?.name || 'Unassigned'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Agent ID</span>
              <span style={{ fontWeight: '600', fontSize: '14px' }}>{user?.agent?.agent_id || '—'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Role Scope</span>
              <span className="badge info">{user?.role}</span>
            </div>
          </div>
          <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => navigate('/ai-assistant')}>
            Invoke AI Assistant
          </button>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3>My Recent AI Activity</h3>
          </div>
          <div className="empty-state">
            Your recent AI activity feed will appear here when the audit engine is enabled.
          </div>
        </div>
      </div>

      {loading && <PageLoader overlay={true} message="Refreshing..." delay={500} />}
    </div>
  );
};

export default UserDashboard;
