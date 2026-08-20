import React, { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';

const Settings = () => {
  const { user } = useContext(AuthContext);
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState(null);

  if (!user) return null;

  const handleSave = async () => {
    setSaving(true);
    setFeedback(null);

    // No backend endpoint for updating profile currently exists
    setTimeout(() => {
      setSaving(false);
      setFeedback({ type: 'error', message: 'Profile editing is not yet supported by the backend API. Contact your administrator.' });
    }, 500);
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
