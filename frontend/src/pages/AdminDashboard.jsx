import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const { token, user } = useContext(AuthContext);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/admin/dashboard-stats`, {
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
        <p style={{color: 'var(--text-muted)', margin: '5px 0 0 0'}}>Here's what's happening with your CRM agents today.</p>
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
              <span className="stat-title">Active AI Sessions</span>
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
                <h3>Governance Overview</h3>
              </div>
              <div style={{marginBottom: '15px'}}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '5px'}}>
                  <span>Total Portal Users</span>
                  <span style={{fontWeight: 'bold'}}>{stats.total_users}</span>
                </div>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '5px'}}>
                  <span>Active Users</span>
                  <span style={{fontWeight: 'bold'}}>{stats.active_users}</span>
                </div>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '5px'}}>
                  <span>Active Agents</span>
                  <span style={{fontWeight: 'bold'}}>{stats.total_agents}</span>
                </div>
              </div>
              
              {stats.pending_signups > 0 ? (
                <div style={{backgroundColor: '#fff3cd', padding: '15px', borderRadius: '4px', border: '1px solid #ffeeba'}}>
                  <h4 style={{margin: '0 0 10px 0', color: '#856404'}}>Pending Action Required</h4>
                  <p style={{margin: '0 0 15px 0', color: '#856404', fontSize: '0.9rem'}}>
                    There are {stats.pending_signups} new signup requests waiting for your approval.
                  </p>
                  <button className="btn" style={{backgroundColor: '#ffc107', color: '#000'}} onClick={() => navigate('/signup-requests')}>
                    Review Requests
                  </button>
                </div>
              ) : (
                <div style={{backgroundColor: '#d4edda', padding: '15px', borderRadius: '4px', border: '1px solid #c3e6cb'}}>
                  <h4 style={{margin: '0', color: '#155724', fontSize: '0.95rem'}}>All Caught Up</h4>
                  <p style={{margin: '5px 0 0 0', color: '#155724', fontSize: '0.85rem'}}>No pending signup requests.</p>
                </div>
              )}
            </div>

            <div className="panel" style={{flex: '2 1 400px'}}>
              <div className="panel-header">
                <h3>Recent AI Activity</h3>
              </div>
              <div style={{padding: '30px', textAlign: 'center', color: 'var(--text-muted)'}}>
                <span style={{fontSize: '2rem'}}>📋</span>
                <p>Detailed AI activity feed will appear here when the Permission Proxy audit engine is fully connected.</p>
              </div>
            </div>
            
            <div className="panel" style={{flex: '1 1 300px'}}>
              <div className="panel-header">
                <h3>Security Overview</h3>
              </div>
              <div style={{padding: '30px', textAlign: 'center', color: 'var(--text-muted)'}}>
                <span style={{fontSize: '2rem'}}>🛡️</span>
                <p>Security alerts and blocked operation metrics will be displayed here in the next phase.</p>
                <button className="btn btn-outline btn-sm" style={{marginTop: '10px'}} onClick={() => navigate('/security-alerts')}>
                  View Alerts
                </button>
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

export default AdminDashboard;
