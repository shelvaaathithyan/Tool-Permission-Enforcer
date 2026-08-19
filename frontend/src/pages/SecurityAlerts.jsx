import React from 'react';

const SecurityAlerts = () => {
  return (
    <div>
      <div className="panel">
        <div className="panel-header">
          <h3>Security Alerts</h3>
        </div>
        <div style={{padding: '60px 20px', textAlign: 'center', color: 'var(--text-muted)'}}>
          <span style={{fontSize: '4rem', opacity: 0.5}}>🛡️</span>
          <h4 style={{marginTop: '20px', fontSize: '1.2rem', color: 'var(--text-color)'}}>No Active Security Alerts</h4>
          <p style={{maxWidth: '400px', margin: '10px auto 0'}}>
            The AI Permission Proxy is not yet enforcing rules. Once enabled, high-severity alerts (such as repeated blocked operations) will appear here.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SecurityAlerts;
