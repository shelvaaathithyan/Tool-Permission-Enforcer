import React, { useContext, useState, useRef, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';

const AiAssistant = () => {
  const { user, token } = useContext(AuthContext);
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionLoading, setSessionLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/auth/session`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setIsSessionActive(data.status === 'ACTIVE');
        } else {
          setIsSessionActive(false);
        }
      } catch (err) {
        setIsSessionActive(false);
      }
      setSessionLoading(false);
    };
    if (token) {
      checkSession();
    }
  }, [token, API_URL]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || !isSessionActive) return;

    const userMessage = { sender: 'user', text: prompt, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    const currentPrompt = prompt;
    setPrompt('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/v1/agent/invoke`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: currentPrompt
        })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        const agentMessage = {
          sender: 'agent',
          text: data.response || "I processed your request.",
          toolRequest: data.tool_request,
          status: data.status,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, agentMessage]);
      } else {
        const errorMessage = {
          sender: 'agent',
          text: `Error: ${data.detail || 'An error occurred'}`,
          status: 'ERROR',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (err) {
      const errorMessage = {
        sender: 'agent',
        text: `Error connecting to agent: ${err.message}`,
        status: 'ERROR',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', height: 'calc(100vh - 140px)'}}>
      {/* Header */}
      <div className="card-row" style={{marginBottom: '20px', flexShrink: 0}}>
        <div className="stat-card">
          <span className="stat-title">Current Agent</span>
          <span className="stat-value" style={{fontSize: '1.2rem'}}>{user?.agent?.name || 'Unassigned'}</span>
          <span style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Agent ID: {user?.agent?.agent_id || '—'}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Portal Session</span>
          <span className="stat-value" style={{fontSize: '1.2rem', color: sessionLoading ? 'var(--text-muted)' : (isSessionActive ? 'var(--success-color)' : 'var(--danger-color)')}}>
            {sessionLoading ? '● CHECKING...' : (isSessionActive ? '● ACTIVE' : '● INACTIVE')}
          </span>
          <span style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>
            {sessionLoading ? 'Verifying...' : (isSessionActive ? 'Ready for operations' : 'Agent operations unavailable')}
          </span>
        </div>
      </div>

      {/* Chat Area */}
      <div className="panel" style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden'}}>
        <div className="panel-header" style={{flexShrink: 0}}>
          <h3>AI Assistant Conversation</h3>
        </div>
        
        {/* Messages */}
        <div style={{flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px'}}>
          {messages.length === 0 && (
            <div style={{textAlign: 'center', color: 'var(--text-muted)', marginTop: '40px'}}>
              <span style={{fontSize: '3rem'}}>💬</span>
              <h4>How can I help you today?</h4>
              <p>Try asking me to "Show me Karthikeyan VV" or "List all customers".</p>
            </div>
          )}
          
          {messages.map((msg, index) => (
            <div key={index} style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <div style={{
                maxWidth: '80%',
                padding: '15px',
                borderRadius: '8px',
                backgroundColor: msg.sender === 'user' ? 'var(--primary-color)' : 'var(--bg-color)',
                color: msg.sender === 'user' ? '#fff' : 'inherit',
                border: msg.sender === 'agent' ? '1px solid var(--border-color)' : 'none'
              }}>
                <div style={{fontSize: '0.8rem', opacity: 0.8, marginBottom: '5px'}}>
                  {msg.sender === 'user' ? user.name : (user?.agent?.name || 'Agent')} • {msg.timestamp.toLocaleTimeString()}
                </div>
                <div style={{whiteSpace: 'pre-wrap', lineHeight: '1.5'}}>{msg.text}</div>
                
                {/* Tool Request Card */}
                {msg.toolRequest && (
                  <div style={{
                    marginTop: '15px',
                    backgroundColor: '#fff',
                    color: '#333',
                    borderRadius: '6px',
                    border: '1px solid #ddd',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      backgroundColor: '#f8f9fa',
                      padding: '10px 15px',
                      borderBottom: '1px solid #ddd',
                      fontWeight: 'bold',
                      fontSize: '0.9rem',
                      display: 'flex',
                      justifyContent: 'space-between'
                    }}>
                      <span>[ TOOL REQUEST ]</span>
                      {msg.status === 'PENDING_PERMISSION_PROXY' && <span style={{color: '#856404'}}>WAITING FOR PERMISSION PROXY</span>}
                      {msg.status === 'BLOCKED' && <span style={{color: '#721c24'}}>✕ BLOCKED</span>}
                    </div>
                    <div style={{padding: '15px', fontSize: '0.9rem'}}>
                      <div style={{marginBottom: '5px'}}><strong>Operation:</strong> {msg.toolRequest.operation}</div>
                      <div style={{marginBottom: '5px'}}><strong>Resource:</strong> {msg.toolRequest.resource}</div>
                      <div style={{marginBottom: '5px'}}><strong>Tool:</strong> {msg.toolRequest.tool_name}</div>
                      
                      {msg.toolRequest.arguments && Object.keys(msg.toolRequest.arguments).length > 0 && (
                        <div style={{marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #eee'}}>
                          <strong>Arguments:</strong>
                          <pre style={{margin: '5px 0 0 0', backgroundColor: '#f4f4f4', padding: '10px', borderRadius: '4px', fontSize: '0.8rem'}}>
                            {JSON.stringify(msg.toolRequest.arguments, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                    {msg.status === 'BLOCKED' && (
                      <div style={{padding: '10px 15px', backgroundColor: '#f8d7da', color: '#721c24', borderTop: '1px solid #f5c6cb', fontSize: '0.9rem'}}>
                        <strong>Reason:</strong> Agent {msg.toolRequest.operation} operations are not permitted.
                      </div>
                    )}
                  </div>
                )}
                
                {/* Visual Architecture Indicator */}
                {msg.sender === 'agent' && msg.status === 'PENDING_PERMISSION_PROXY' && (
                  <div style={{marginTop: '15px', fontSize: '0.8rem', color: '#6c757d', display: 'flex', alignItems: 'center', gap: '5px'}}>
                    <span style={{fontWeight: 'bold'}}>Agent</span> 
                    <span>→</span> 
                    <span style={{fontWeight: 'bold', color: '#ffc107'}}>Permission Proxy</span> 
                    <span>→</span> 
                    <span style={{opacity: 0.5}}>CRM</span>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{padding: '20px', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-color)', flexShrink: 0}}>
          {!isSessionActive ? (
            <div style={{textAlign: 'center', color: 'var(--danger-color)', padding: '10px'}}>
              Your Agent session is inactive. Agent operations are unavailable.
            </div>
          ) : (
            <form onSubmit={handleSend} style={{display: 'flex', gap: '10px'}}>
              <input
                type="text"
                className="form-control"
                style={{flex: 1}}
                placeholder="Ask the CRM Agent anything..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                disabled={loading}
              />
              <button type="submit" className="btn btn-primary" disabled={loading || !prompt.trim()}>
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default AiAssistant;

