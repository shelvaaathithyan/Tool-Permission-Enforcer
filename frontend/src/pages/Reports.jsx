import React from 'react';

const Reports = () => {
  return (
    <div>
      <div className="panel">
        <div className="panel-header">
          <h3>Reports</h3>
        </div>
        <div style={{padding: '40px', textAlign: 'center', color: 'var(--text-muted)'}}>
          <span style={{fontSize: '3rem'}}>📊</span>
          <h4>No reports generated</h4>
          <p>The reporting module is scheduled for a future phase.</p>
        </div>
      </div>
    </div>
  );
};

export default Reports;
