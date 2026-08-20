import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import PageLoader from '../components/PageLoader';
import ErrorState from '../components/ErrorState';

const Agents = () => {
  const { token } = useContext(AuthContext);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchAgents = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/agents`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setAgents(await res.json());
      } else {
        setError('Failed to load agents.');
      }
    } catch (e) {
      console.error(e);
      setError('A network error occurred.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, [token]);

  return (
    <div>
      <div className="panel" style={{ position: 'relative', minHeight: '200px' }}>
        <div className="panel-header">
          <h3>AI Agents</h3>
          <button className="btn btn-secondary btn-sm" onClick={fetchAgents} disabled={loading}>Refresh</button>
        </div>

        {error ? (
          <ErrorState message={error} onRetry={fetchAgents} />
        ) : (
          <>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Agent ID</th>
                    <th>Agent Name</th>
                    <th>Owner</th>
                    <th>Owner Role</th>
                    <th>Status</th>
                    <th>Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {!loading && agents.length === 0 ? (
                    <tr><td colSpan="6" className="empty-state">No agents found.</td></tr>
                  ) : (
                    agents.map(a => (
                      <tr key={a.id}>
                        <td>{a.agent_id}</td>
                        <td>{a.name}</td>
                        <td>{a.owner_name || '—'}</td>
                        <td>
                          {a.owner_role && (
                            <span className={`badge ${a.owner_role === 'ADMIN' ? 'danger' : a.owner_role === 'MANAGER' ? 'warning' : 'info'}`}>
                              {a.owner_role}
                            </span>
                          )}
                        </td>
                        <td>
                          <span className={`badge ${a.is_active ? 'success' : 'secondary'}`}>
                            {a.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>{new Date(a.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            {loading && <PageLoader overlay={true} message="Loading agents..." />}
          </>
        )}
      </div>
    </div>
  );
};

export default Agents;
