import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const AuditLogs = () => {
  const { token } = useContext(AuthContext);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/api/v1/audit/logs`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setLogs(data);
        } else if (res.status === 401) {
          setError("Unauthorized. Please log in.");
        } else if (res.status === 403) {
          setError("Forbidden. Admin access required.");
        } else {
          setError("Failed to load audit logs.");
        }
      } catch (e) {
        console.error(e);
        setError("Network error.");
      }
      setLoading(false);
    };
    fetchLogs();
  }, [token]);

  return (
    <div>
      <div className="panel">
        <div className="panel-header">
          <h3>Audit Logs</h3>
        </div>
        
        {loading && <div style={{padding: '20px'}}>Loading...</div>}
        {error && <div style={{padding: '20px', color: 'var(--danger-color)'}}>{error}</div>}
        
        {!loading && !error && (
          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Session</th>
                  <th>Operation</th>
                  <th>Tool</th>
                  <th>Customer</th>
                  <th>Decision</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr><td colSpan="7">No audit logs found.</td></tr>
                ) : (
                  logs.map(log => (
                    <tr key={log.id}>
                      <td>{new Date(log.created_at).toLocaleString()}</td>
                      <td>{log.session_id || '—'}</td>
                      <td>{log.operation}</td>
                      <td>{log.tool_name || '—'}</td>
                      <td>{log.customer_id || '—'}</td>
                      <td>
                        {log.decision === 'ALLOWED' && <span className="badge success">ALLOWED</span>}
                        {log.decision === 'BLOCKED' && <span className="badge danger">BLOCKED</span>}
                        {log.decision === 'PENDING' && <span className="badge secondary">PENDING</span>}
                      </td>
                      <td>{log.reason || '—'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogs;
