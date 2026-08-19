import React from 'react';

const SecurityAlerts = () => {
  return (
    <div>
      <div className="panel">
        <div className="panel-header">
          <h3>Security Alerts</h3>
        </div>
        <div style={{padding: '40px', textAlign: 'center', color: 'var(--text-muted)'}}>
          <span style={{fontSize: '3rem'}}>🛡️</span>
          <h4>No security alerts</h4>
          <p>The backend security rules engine is scheduled for a future phase.</p>
        </div>
      </div>
    </div>
  );
};

export default SecurityAlerts;
