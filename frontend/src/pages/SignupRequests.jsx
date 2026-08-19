import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const SignupRequests = () => {
  const { token } = useContext(AuthContext);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchRequests = async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/signup-requests`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setRequests(data);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchRequests();
  }, [token]);

  const handleApprove = async (id, role) => {
    setActionLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/signup-requests/${id}/approve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ role })
      });
      if (res.ok) fetchRequests();
      else alert("Failed to approve request");
    } catch (e) {
      console.error(e);
    }
    setActionLoading(false);
  };

  const handleReject = async (id) => {
    const reason = prompt("Optional rejection reason:");
    if (reason === null) return;
    setActionLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/admin/signup-requests/${id}/reject`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      if (res.ok) fetchRequests();
      else alert("Failed to reject request");
    } catch (e) {
      console.error(e);
    }
    setActionLoading(false);
  };

  return (
    <div>
      <div className="panel">
        <div className="panel-header">
          <h3>Pending Signup Requests</h3>
          <button className="btn btn-outline" onClick={fetchRequests}>Refresh</button>
        </div>
        
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Requested Role</th>
                <th>Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6">Loading...</td></tr>
              ) : requests.length === 0 ? (
                <tr><td colSpan="6">No signup requests found.</td></tr>
              ) : (
                requests.map(req => (
                  <tr key={req.id}>
                    <td>{req.name}</td>
                    <td>{req.email}</td>
                    <td>{req.requested_role}</td>
                    <td>{new Date(req.created_at).toLocaleDateString()}</td>
                    <td>
                      <span className={`badge ${req.status === 'PENDING' ? 'warning' : req.status === 'APPROVED' ? 'success' : 'danger'}`}>
                        {req.status}
                      </span>
                    </td>
                    <td>
                      {req.status === 'PENDING' && (
                        <div style={{display: 'flex', gap: '5px'}}>
                          <button disabled={actionLoading} onClick={() => handleApprove(req.id, req.requested_role)} className="btn btn-primary btn-sm">
                            Approve ({req.requested_role})
                          </button>
                          <button disabled={actionLoading} onClick={() => handleApprove(req.id, req.requested_role === 'STAFF' ? 'MANAGER' : 'STAFF')} className="btn btn-outline btn-sm">
                            Approve ({req.requested_role === 'STAFF' ? 'MANAGER' : 'STAFF'})
                          </button>
                          <button disabled={actionLoading} onClick={() => handleReject(req.id)} className="btn btn-danger btn-sm">Reject</button>
                        </div>
                      )}
                    </td>
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

export default SignupRequests;
