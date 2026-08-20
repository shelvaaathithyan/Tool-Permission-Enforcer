import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import PageLoader from '../components/PageLoader';
import ErrorState from '../components/ErrorState';

const AdminDashboard = () => {
  const { token, user } = useContext(AuthContext);
  const navigate = useNavigate();
  
  const [data, setData] = useState({
    stats: null,
    recentCustomers: [],
    teamMembers: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Fetch independent data concurrently
      const [statsRes, customersRes, usersRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/admin/dashboard-stats`, { headers }),
        fetch(`${API_URL}/api/v1/crm/customers?page=1&page_size=5`, { headers }),
        fetch(`${API_URL}/api/v1/admin/users`, { headers })
      ]);

      if (!statsRes.ok || !customersRes.ok || !usersRes.ok) {
        throw new Error('One or more API requests failed.');
      }

      const [statsData, customersData, usersData] = await Promise.all([
        statsRes.json(),
        customersRes.json(),
        usersRes.json()
      ]);

      // Process team members (filter for staff/managers)
      const team = usersData
        .filter(u => u.is_active && (u.role === 'STAFF' || u.role === 'MANAGER' || u.role === 'ADMIN'))
        .slice(0, 5); // take latest 5 for overview

      setData({
        stats: statsData,
        recentCustomers: customersData.items || [],
        teamMembers: team
      });
    } catch (e) {
      console.error(e);
      setError('Unable to load dashboard data. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [token]);

  if (loading && !data.stats) {
    return <PageLoader message="Loading dashboard..." delay={250} />;
  }

  if (error && !data.stats) {
    return <ErrorState message={error} onRetry={fetchDashboardData} />;
  }

  const { stats, recentCustomers, teamMembers } = data;

  return (
    <div style={{ position: 'relative', minHeight: '300px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: 0 }}>
          {user?.name ? `Welcome, ${user.name}` : (user?.role === 'ADMIN' ? 'Welcome, System Administrator' : 'Welcome')}
        </h2>
        <p style={{ color: 'var(--text-muted)', margin: '5px 0 0 0' }}>Here's what's happening across your CRM today.</p>
      </div>

      <div className="card-row">
        <div className="stat-card" style={{ alignItems: 'center', textAlign: 'center' }}>
          <span className="stat-title">Total Customers</span>
          <span className="stat-value">{stats?.total_customers || 0}</span>
        </div>
        <div className="stat-card" style={{ alignItems: 'center', textAlign: 'center' }}>
          <span className="stat-title">Active Staff/Users</span>
          <span className="stat-value">{stats?.active_users || 0}</span>
        </div>
        <div className="stat-card" style={{ alignItems: 'center', textAlign: 'center' }}>
          <span className="stat-title">Active Agents</span>
          <span className="stat-value">{stats?.total_agents || 0}</span>
        </div>
        <div className="stat-card" style={{ alignItems: 'center', textAlign: 'center', borderLeft: stats?.pending_signups > 0 ? '4px solid #ffc107' : '' }}>
          <span className="stat-title">Pending Signups</span>
          <span className="stat-value" style={{ color: stats?.pending_signups > 0 ? '#856404' : 'inherit' }}>
            {stats?.pending_signups || 0}
          </span>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Customer Overview Panel */}
        <div className="panel">
          <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>Recent Customers</h3>
            <button className="btn btn-sm btn-secondary" onClick={() => navigate('/customers')}>View All</button>
          </div>
          
          {recentCustomers.length === 0 ? (
            <div className="empty-state">No customers found.</div>
          ) : (
            <ul className="mini-list">
              {recentCustomers.map(c => (
                <li key={c.id} className="mini-list-item">
                  <div>
                    <div style={{ fontWeight: '500' }}>{c.first_name} {c.last_name}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{c.email}</div>
                  </div>
                  <div>
                    {c.session_status === 'ACTIVE' ? (
                      <span className="badge success">Active</span>
                    ) : (
                      <span className="badge danger">Inactive</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Team Overview Panel */}
        <div className="panel">
          <div className="panel-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>Team Overview</h3>
            <button className="btn btn-sm btn-secondary" onClick={() => navigate('/users')}>View Team</button>
          </div>
          
          {teamMembers.length === 0 ? (
            <div className="empty-state">No active team members.</div>
          ) : (
            <ul className="mini-list">
              {teamMembers.map(tm => (
                <li key={tm.id} className="mini-list-item">
                  <div>
                    <div style={{ fontWeight: '500' }}>{tm.name}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{tm.role}</div>
                  </div>
                  <div>
                    {tm.agent_id ? (
                      <span className="badge info">Has Agent</span>
                    ) : (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No Agent</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      
      {/* Pending signups alert block */}
      {stats?.pending_signups > 0 && (
        <div className="dashboard-grid">
          <div className="panel" style={{ backgroundColor: '#fff3cd', borderColor: '#ffeeba' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px' }}>
              <div>
                <h4 style={{ margin: '0 0 5px 0', color: '#856404' }}>Action Required</h4>
                <p style={{ margin: 0, color: '#856404', fontSize: '0.9rem' }}>
                  There are {stats.pending_signups} new signup requests waiting for your approval.
                </p>
              </div>
              <button className="btn" style={{ backgroundColor: '#ffc107', color: '#000', border: 'none' }} onClick={() => navigate('/signup-requests')}>
                Review Requests
              </button>
            </div>
          </div>
        </div>
      )}

      {loading && <PageLoader overlay={true} message="Refreshing dashboard..." delay={500} />}
    </div>
  );
};

export default AdminDashboard;

