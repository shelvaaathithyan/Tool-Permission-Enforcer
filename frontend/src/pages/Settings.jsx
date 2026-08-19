import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const Settings = () => {
  const { user } = useContext(AuthContext);

  if (!user) return null;

  return (
    <div>
      <div className="panel" style={{maxWidth: '600px'}}>
        <div className="panel-header">
          <h3>Account Settings</h3>
        </div>
        
        <div className="form-group">
          <label>Name</label>
          <input type="text" className="form-control" value={user.name || ''} disabled />
        </div>
        
        <div className="form-group">
          <label>Email</label>
          <input type="email" className="form-control" value={user.email || ''} disabled />
        </div>
        
        <div className="form-group">
          <label>Role</label>
          <input type="text" className="form-control" value={user.role || ''} disabled />
          <small style={{color: 'var(--text-muted)'}}>Role cannot be changed from the frontend.</small>
        </div>
        
        <div className="form-group">
          <label>Agent ID</label>
          <input type="text" className="form-control" value={user.agent?.agent_id || 'None'} disabled />
          <small style={{color: 'var(--text-muted)'}}>Agent assignment is managed by the system admin.</small>
        </div>
      </div>
    </div>
  );
};

export default Settings;
