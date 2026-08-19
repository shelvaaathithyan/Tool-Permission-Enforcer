import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const SecurityAlerts = () => {
  const { token } = useContext(AuthContext);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/api/v1/audit/alerts`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setAlerts(data);
        } else if (res.status === 401) {
          setError("Unauthorized. Please log in.");
        } else if (res.status === 403) {
          setError("Forbidden. Admin access required.");
        } else {
          setError("Failed to load security alerts.");
        }
      } catch (e) {
        console.error(e);
        setError("Network error.");
      }
      setLoading(false);
    };
    fetchAlerts();
  }, [token]);

  return (
    <div>
      <div className="panel">
        <div className="panel-header">
          <h3>Security Alerts</h3>
        </div>

        {loading && <div style={{padding: '20px'}}>Loading...</div>}
        {error && <div style={{padding: '20px', color: 'var(--danger-color)'}}>{error}</div>}

        {!loading && !error && (
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
                {alerts.length === 0 ? (
                  <tr><td colSpan="5">No active security alerts.</td></tr>
                ) : (
                  alerts.map(alert => (
                    <tr key={alert.id}>
                      <td>{new Date(alert.created_at).toLocaleString()}</td>
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
                      <td>{alert.session_id || '—'}</td>
                      <td style={alert.severity === 'HIGH' && alert.status === 'OPEN' ? {fontWeight: 'bold', color: 'var(--danger-color)'} : {}}>
                        {alert.description}
                      </td>
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

export default SecurityAlerts;
