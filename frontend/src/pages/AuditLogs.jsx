import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import PageLoader from '../components/PageLoader';
import ErrorState from '../components/ErrorState';

const AuditLogs = () => {
  const { token } = useContext(AuthContext);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/audit/logs`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setLogs(await res.json());
      } else if (res.status === 401) {
        setError('Unauthorized. Please log in.');
      } else if (res.status === 403) {
        setError('Forbidden. Admin access required.');
      } else {
        setError('Failed to load audit logs.');
      }
    } catch (e) {
      console.error(e);
      setError('A network error occurred.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [token]);

  return (
    <div>
      <div className="panel" style={{ position: 'relative', minHeight: '200px' }}>
        <div className="panel-header">
          <h3>Audit Logs</h3>
          <button className="btn btn-secondary btn-sm" onClick={fetchLogs} disabled={loading}>Refresh</button>
        </div>

        {error ? (
          <ErrorState message={error} onRetry={fetchLogs} />
        ) : (
          <>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Session</th>
                    <th>Operation</th>
                    <th>Tool</th>
                    <th>Agent</th>
                    <th>Decision</th>
                    <th>Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {!loading && logs.length === 0 ? (
                    <tr><td colSpan="7" className="empty-state">No audit logs found.</td></tr>
                  ) : (
                    logs.map(log => (
                      <tr key={log.id}>
                        <td style={{ whiteSpace: 'nowrap' }}>{new Date(log.created_at).toLocaleString()}</td>
                        <td style={{ fontSize: '12px' }}>{log.session_id || '—'}</td>
                        <td>{log.operation}</td>
                        <td>{log.tool_name || '—'}</td>
                        <td>
                          <div style={{ fontWeight: '500' }}>{log.agent_name || 'Unknown Agent'}</div>
                          {log.agent_id && <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{log.agent_id}</div>}
                        </td>
                        <td>
                          {log.decision === 'ALLOWED' && <span className="badge success">ALLOWED</span>}
                          {log.decision === 'BLOCKED' && <span className="badge danger">BLOCKED</span>}
                        </td>
                        <td style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }}>{log.reason || '—'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            {loading && <PageLoader overlay={true} message="Loading audit logs..." />}
          </>
        )}
      </div>
    </div>
  );
};

export default AuditLogs;
