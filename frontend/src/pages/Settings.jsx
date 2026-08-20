import React, { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';

const Settings = () => {
  const { user, token, setUser } = useContext(AuthContext);
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(null);

  if (!user) return null;

  const handleSave = async () => {
    const trimmedName = name.trim();
    if (!trimmedName) {
      setFeedback({ type: 'error', message: 'Name cannot be empty.' });
      return;
    }

    setSaving(true);
    setFeedback(null);

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_URL}/api/v1/auth/me`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: trimmedName })
      });

      if (res.ok) {
        const updatedUser = await res.json();
        setUser(updatedUser);
        setFeedback({ type: 'success', message: 'Profile updated successfully.' });
      } else {
        const data = await res.json();
        setFeedback({ type: 'error', message: data.detail || 'Unable to update your profile. Please try again.' });
      }
    } catch (err) {
      setFeedback({ type: 'error', message: 'Unable to update your profile. Please check your connection and try again.' });
    } finally {
      setSaving(false);
    }
  };

  const hasChanges = name !== (user.name || '');

  return (
    <div className="settings-container">
      <div className="panel">
        <div className="panel-header">
          <h3>Account Settings</h3>
        </div>
        
        {feedback && (
          <div className={`settings-feedback ${feedback.type}`}>
            {feedback.message}
          </div>
        )}

        <div className="settings-section">
          <div className="settings-section-title">Profile Information</div>
          
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label htmlFor="settings-name">Name</label>
            <input
              id="settings-name"
              type="text"
              className="form-control"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
        </div>

        <div className="settings-section">
          <div className="settings-section-title">Account Details</div>
          
          <div className="settings-row">
            <span className="settings-label">Email</span>
            <span className="settings-value" style={{ color: 'var(--text-muted)' }}>{user.email}</span>
          </div>

          <div className="settings-row">
            <span className="settings-label">Role</span>
            <span className={`badge ${user.role === 'ADMIN' ? 'danger' : user.role === 'MANAGER' ? 'warning' : 'info'}`}>
              {user.role}
            </span>
          </div>

          <div className="settings-row">
            <span className="settings-label">Agent ID</span>
            <span className="settings-value">{user.agent?.agent_id || 'None'}</span>
          </div>

          <div className="settings-row">
            <span className="settings-label">Agent Name</span>
            <span className="settings-value">{user.agent?.name || '—'}</span>
          </div>
        </div>

        <div className="settings-actions">
          <button className="btn btn-primary" onClick={handleSave} disabled={saving || !hasChanges}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
