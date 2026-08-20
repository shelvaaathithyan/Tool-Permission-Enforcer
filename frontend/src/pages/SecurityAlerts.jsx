import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import PageLoader from '../components/PageLoader';
import ErrorState from '../components/ErrorState';

const SecurityAlerts = () => {
  const { token } = useContext(AuthContext);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/audit/alerts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setAlerts(await res.json());
      } else if (res.status === 401) {
        setError('Unauthorized. Please log in.');
      } else if (res.status === 403) {
        setError('Forbidden. Admin access required.');
      } else {
        setError('Failed to load security alerts.');
      }
    } catch (e) {
      console.error(e);
      setError('A network error occurred.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [token]);

  return (
    <div>
      <div className="panel" style={{ position: 'relative', minHeight: '200px' }}>
        <div className="panel-header">
          <h3>Security Alerts</h3>
          <button className="btn btn-secondary btn-sm" onClick={fetchAlerts} disabled={loading}>Refresh</button>
        </div>

        {error ? (
          <ErrorState message={error} onRetry={fetchAlerts} />
        ) : (
          <>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Session</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {!loading && alerts.length === 0 ? (
                    <tr><td colSpan="5" className="empty-state">No active security alerts.</td></tr>
                  ) : (
                    alerts.map(alert => (
                      <tr key={alert.id}>
                        <td style={{ whiteSpace: 'nowrap' }}>{new Date(alert.created_at).toLocaleString()}</td>
                        <td>
                          <span className={`badge ${alert.severity === 'HIGH' ? 'danger' : 'secondary'}`}>
                            {alert.severity}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${alert.status === 'OPEN' ? 'warning' : 'success'}`}>
                            {alert.status}
                          </span>
                        </td>
                        <td style={{ fontSize: '12px' }}>{alert.session_id || '—'}</td>
                        <td style={alert.severity === 'HIGH' && alert.status === 'OPEN' ? { fontWeight: '500', color: 'var(--danger-color)' } : {}}>
                          {alert.description}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            {loading && <PageLoader overlay={true} message="Loading alerts..." />}
          </>
        )}
      </div>
    </div>
  );
};

export default SecurityAlerts;
