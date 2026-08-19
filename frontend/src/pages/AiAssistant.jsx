import React, { useContext, useState, useRef, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import AssistantMessage from '../components/assistant/AssistantMessage';
import ErrorBoundary from '../components/ErrorBoundary';

const AiAssistant = () => {
  const { user, token } = useContext(AuthContext);
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const [isSessionActive, setIsSessionActive] = useState(false);
  const [sessionLoading, setSessionLoading] = useState(true);
  const [currentSessionId, setCurrentSessionId] = useState(null);

  // Load chat history from sessionStorage
  useEffect(() => {
    if (user?.id) {
      const saved = sessionStorage.getItem(`crm_agent_chat_${user.id}`);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (Array.isArray(parsed)) {
            const restored = parsed.reduce((acc, msg) => {
              if (msg && typeof msg === 'object' && msg.sender) {
                let ts = new Date();
                if (msg.timestamp) {
                  const d = new Date(msg.timestamp);
                  if (!isNaN(d.getTime())) ts = d;
                }
                acc.push({ ...msg, timestamp: ts });
              }
              return acc;
            }, []);
            setMessages(restored);
          }
        } catch (e) {
          console.error("Failed to parse chat history safely");
        }
      }
    }
  }, [user?.id]);

  // Save chat history to sessionStorage
  useEffect(() => {
    if (user?.id && messages.length > 0) {
      sessionStorage.setItem(`crm_agent_chat_${user.id}`, JSON.stringify(messages));
    }
  }, [messages, user?.id]);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/auth/session`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setIsSessionActive(data.status === 'ACTIVE');
          setCurrentSessionId(data.session_id);
        } else {
          setIsSessionActive(false);
          setCurrentSessionId(null);
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
      
      
      let data = {};
      let isJsonError = false;
      try {
        data = await res.json();
      } catch (e) {
        data = { detail: "Invalid JSON response from server" };
        isJsonError = true;
      }
      
      if (res.ok && !isJsonError && data && typeof data === 'object') {
        const agentMessage = {
          sender: 'agent',
          text: data.response || "I processed your request.",
          toolRequest: data.tool_request || null,
          status: data.status || 'UNKNOWN',
          decision: data.decision || null,
          reason: data.reason || null,
          result: data.result || null,
          sessionId: currentSessionId,
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
                {msg.sender === 'user' ? (
                  <div style={{whiteSpace: 'pre-wrap', lineHeight: '1.5'}}>{msg.text}</div>
                ) : (
                  <ErrorBoundary>
                    <AssistantMessage msg={msg} user={user} currentSessionId={currentSessionId} />
                  </ErrorBoundary>
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

