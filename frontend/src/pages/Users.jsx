import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import PageLoader from '../components/PageLoader';
import ErrorState from '../components/ErrorState';

const Users = () => {
  const { token } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setUsers(await res.json());
      } else {
        setError('Failed to load users.');
      }
    } catch (e) {
      console.error(e);
      setError('A network error occurred.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [token]);

  return (
    <div>
      <div className="panel" style={{ position: 'relative', minHeight: '200px' }}>
        <div className="panel-header">
          <h3>Portal Users</h3>
          <button className="btn btn-secondary btn-sm" onClick={fetchUsers} disabled={loading}>Refresh</button>
        </div>

        {error ? (
          <ErrorState message={error} onRetry={fetchUsers} />
        ) : (
          <>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Agent</th>
                    <th>Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {!loading && users.length === 0 ? (
                    <tr><td colSpan="6" className="empty-state">No users found.</td></tr>
                  ) : (
                    users.map(u => (
                      <tr key={u.id}>
                        <td>{u.name}</td>
                        <td>{u.email}</td>
                        <td><span className={`badge ${u.role === 'ADMIN' ? 'danger' : u.role === 'MANAGER' ? 'warning' : 'info'}`}>{u.role}</span></td>
                        <td>
                          <span className={`badge ${u.is_active ? 'success' : 'secondary'}`}>
                            {u.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>{u.agent_name ? `${u.agent_name} (${u.agent_id})` : '—'}</td>
                        <td>{new Date(u.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            {loading && <PageLoader overlay={true} message="Loading users..." />}
          </>
        )}
      </div>
    </div>
  );
};

export default Users;
