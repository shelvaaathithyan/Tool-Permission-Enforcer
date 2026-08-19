import React, { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';

const AiAssistant = () => {
  const { user, token } = useContext(AuthContext);
  const [operation, setOperation] = useState('read');
  const [targetId, setTargetId] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleInvoke = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const args = operation === 'list' ? {} : { customer_id: targetId };
      const res = await fetch(`${API_URL}/api/v1/agent/invoke`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tool_name: 'crm',
          operation: operation,
          arguments: args
        })
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: String(err) });
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="card-row">
        <div className="stat-card">
          <span className="stat-title">Current Agent</span>
          <span className="stat-value" style={{fontSize: '1.2rem'}}>{user.agent?.name || 'No Agent'}</span>
          <span style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>{user.agent?.agent_id}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Session Status</span>
          <span className="stat-value" style={{fontSize: '1.2rem'}}>ACTIVE</span>
          <span style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Ready for operations</span>
        </div>
      </div>

      <div className="panel" style={{maxWidth: '600px'}}>
        <div className="panel-header">
          <h3>Test Agent Invoke</h3>
        </div>
        <form onSubmit={handleInvoke}>
          <div className="form-group">
            <label>Operation</label>
            <select className="form-control" value={operation} onChange={e => setOperation(e.target.value)}>
              <option value="list">list (List all customers)</option>
              <option value="read">read (Read specific customer)</option>
              <option value="create">create (Create customer)</option>
              <option value="update">update (Update customer)</option>
              <option value="delete">delete (Delete customer)</option>
            </select>
          </div>
          {operation !== 'list' && (
            <div className="form-group">
              <label>Target Customer ID (optional for create)</label>
              <input type="text" className="form-control" value={targetId} onChange={e => setTargetId(e.target.value)} placeholder="e.g. CUST-XXXXX" />
            </div>
          )}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Invoking Agent...' : 'Invoke Tool'}
          </button>
        </form>

        {result && (
          <div style={{marginTop: '20px', padding: '15px', backgroundColor: 'var(--code-bg)', borderRadius: '4px'}}>
            <h4 style={{marginTop: 0}}>Agent Response:</h4>
            <pre style={{margin: 0, whiteSpace: 'pre-wrap', fontSize: '0.85rem'}}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default AiAssistant;
