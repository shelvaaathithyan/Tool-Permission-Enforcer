import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const UserDashboard = () => {
  const { token, user } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/admin/my-stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (e) {
        console.error(e);
      }
      setLoading(false);
    };
    fetchStats();
  }, [token]);

  return (
    <div>
      <div style={{marginBottom: '20px'}}>
        <h2 style={{margin: 0}}>Welcome back, {user?.name}</h2>
        <p style={{color: 'var(--text-muted)', margin: '5px 0 0 0'}}>Here's an overview of your CRM and Agent activity.</p>
      </div>

      {loading ? (
        <p>Loading stats...</p>
      ) : stats ? (
        <>
          <div className="card-row">
            <div className="stat-card">
              <span className="stat-title">Total Customers</span>
              <span className="stat-value">{stats.total_customers}</span>
            </div>
            <div className="stat-card">
              <span className="stat-title">My Active Sessions</span>
              <span className="stat-value">{stats.active_sessions}</span>
            </div>
            <div className="stat-card">
              <span className="stat-title">Allowed Operations</span>
              <span className="stat-value" style={{color: 'var(--success-color)'}}>{stats.allowed_operations}</span>
            </div>
            <div className="stat-card">
              <span className="stat-title">Blocked Operations</span>
              <span className="stat-value" style={{color: 'var(--danger-color)'}}>{stats.blocked_operations}</span>
            </div>
          </div>

          <div style={{display: 'flex', gap: '24px', flexWrap: 'wrap'}}>
            <div className="panel" style={{flex: '1 1 300px'}}>
              <div className="panel-header">
                <h3>My Agent Status</h3>
              </div>
              <div style={{marginBottom: '15px'}}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                  <span style={{color: 'var(--text-muted)'}}>Agent Name:</span>
                  <span style={{fontWeight: 'bold'}}>{user?.agent?.name || 'Unassigned'}</span>
                </div>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                  <span style={{color: 'var(--text-muted)'}}>Agent ID:</span>
                  <span style={{fontWeight: 'bold'}}>{user?.agent?.agent_id || '—'}</span>
                </div>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '10px'}}>
                  <span style={{color: 'var(--text-muted)'}}>Role Scope:</span>
                  <span className="badge info">{user?.role}</span>
                </div>
              </div>
              <div style={{marginTop: '20px'}}>
                <button className="btn btn-primary" style={{width: '100%'}} onClick={() => navigate('/ai-assistant')}>
                  Invoke AI Assistant
                </button>
              </div>
            </div>

            <div className="panel" style={{flex: '2 1 400px'}}>
              <div className="panel-header">
                <h3>My Recent AI Activity</h3>
              </div>
              <div style={{padding: '30px', textAlign: 'center', color: 'var(--text-muted)'}}>
                <p>Your recent AI activity feed will appear here when the audit engine is enabled.</p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <p>Failed to load dashboard data.</p>
      )}
    </div>
  );
};

export default UserDashboard;
