import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const Agents = () => {
  const { token } = useContext(AuthContext);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/agents`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAgents(data);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchAgents();
  }, [token]);

  return (
    <div>
      <div className="panel">
        <div className="panel-header">
          <h3>AI Agents</h3>
          <button className="btn btn-outline" onClick={fetchAgents}>Refresh</button>
        </div>
        
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
              {loading ? (
                <tr><td colSpan="6">Loading...</td></tr>
              ) : agents.length === 0 ? (
                <tr><td colSpan="6">No agents found.</td></tr>
              ) : (
                agents.map(a => (
                  <tr key={a.id}>
                    <td>{a.agent_id}</td>
                    <td>{a.name}</td>
                    <td>{a.owner_name || '—'}</td>
                    <td>
                      {a.owner_role && (
                        <span className={`badge ${a.owner_role === 'ADMIN' ? 'danger' : 'info'}`}>
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
      </div>
    </div>
  );
};

export default Agents;
