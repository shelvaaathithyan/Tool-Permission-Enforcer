import React, { useContext, useState, useRef, useEffect } from 'react';
import { AuthContext } from '../context/AuthContext';
import AssistantMessage from '../components/assistant/AssistantMessage';
import ErrorBoundary from '../components/ErrorBoundary';
import { Bot, Send, User, Sparkles } from 'lucide-react';

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
  }, [messages, loading]);

  const handleSend = async (e, customPrompt = null) => {
    if (e) e.preventDefault();
    const textToSend = customPrompt || prompt;
    if (!textToSend.trim() || !isSessionActive) return;

    const userMessage = { sender: 'user', text: textToSend, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
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
          prompt: textToSend
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

  const handleSuggestion = (text) => {
    handleSend(null, text);
  };

  return (
    <div style={{display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)', maxWidth: '1000px', margin: '0 auto'}}>
      
      {/* Header Info */}
      <div style={{ padding: '0 0 var(--space-4) 0', flexShrink: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', borderBottom: '1px solid var(--border-color)', marginBottom: 'var(--space-4)' }}>
        <div>
          <h2 style={{ margin: '0 0 4px 0', fontSize: '20px' }}>AI Assistant</h2>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '13px' }}>Your CRM intelligence workspace</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', backgroundColor: 'var(--card-bg)', padding: '8px 12px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-color)', boxShadow: 'var(--card-shadow)' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--primary-light)', color: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Bot size={18} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-color)', lineHeight: 1.2 }}>{user?.agent?.name || 'CRM Assistant'}</span>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{user?.agent?.agent_id || 'Unassigned'}</span>
          </div>
          <div style={{ marginLeft: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: sessionLoading ? 'var(--text-light)' : (isSessionActive ? 'var(--success-color)' : 'var(--danger-color)') }}></span>
            <span style={{ fontSize: '11px', fontWeight: 500, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              {sessionLoading ? 'Checking' : (isSessionActive ? 'Active' : 'Inactive')}
            </span>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', backgroundColor: 'var(--card-bg)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--border-color)', boxShadow: 'var(--card-shadow)'}}>
        
        {/* Messages */}
        <div style={{flex: 1, overflowY: 'auto', padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-5)'}}>
          {messages.length === 0 && (
            <div style={{textAlign: 'center', color: 'var(--text-muted)', marginTop: 'var(--space-10)', display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
              <div style={{ width: '48px', height: '48px', borderRadius: '50%', backgroundColor: 'var(--primary-light)', color: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 'var(--space-4)' }}>
                <Sparkles size={24} />
              </div>
              <h4 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-color)', marginBottom: 'var(--space-2)' }}>How can I help you today?</h4>
              <p style={{ fontSize: '13px', marginBottom: 'var(--space-6)', maxWidth: '400px' }}>Ask about customers, staff, agents, permissions, security activity, or CRM data.</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-3)', width: '100%', maxWidth: '600px' }}>
                <button className="btn btn-secondary" style={{ padding: '12px', justifyContent: 'flex-start', textAlign: 'left', fontWeight: 400 }} onClick={() => handleSuggestion('Show me all customers')}>
                  "Show me all customers"
                </button>
                <button className="btn btn-secondary" style={{ padding: '12px', justifyContent: 'flex-start', textAlign: 'left', fontWeight: 400 }} onClick={() => handleSuggestion('Who works at XYXY Company?')}>
                  "Who works at XYXY Company?"
                </button>
                <button className="btn btn-secondary" style={{ padding: '12px', justifyContent: 'flex-start', textAlign: 'left', fontWeight: 400 }} onClick={() => handleSuggestion('Show active staff')}>
                  "Show active staff"
                </button>
                <button className="btn btn-secondary" style={{ padding: '12px', justifyContent: 'flex-start', textAlign: 'left', fontWeight: 400 }} onClick={() => handleSuggestion('List recent customer activity')}>
                  "List recent customer activity"
                </button>
              </div>
            </div>
          )}
          
          {messages.map((msg, index) => (
            <div key={index} style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start'
            }}>
              <div style={{
                maxWidth: '85%',
                padding: '14px 18px',
                borderRadius: '16px',
                borderBottomRightRadius: msg.sender === 'user' ? '4px' : '16px',
                borderBottomLeftRadius: msg.sender === 'agent' ? '4px' : '16px',
                backgroundColor: msg.sender === 'user' ? 'var(--primary-color)' : '#ffffff',
                color: msg.sender === 'user' ? '#ffffff' : 'var(--text-color)',
                border: msg.sender === 'agent' ? '1px solid var(--border-color)' : '1px solid var(--primary-color)',
                boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
              }}>
                <div style={{fontSize: '11px', opacity: msg.sender === 'user' ? 0.8 : 0.5, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '4px'}}>
                  {msg.sender === 'user' ? (
                    <><User size={12} /> You</>
                  ) : (
                    <><Bot size={12} /> CRM Assistant</>
                  )}
                  <span style={{ margin: '0 4px' }}>•</span>
                  {msg.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
                {msg.sender === 'user' ? (
                  <div style={{whiteSpace: 'pre-wrap', lineHeight: '1.5', fontSize: '14px'}}>{msg.text}</div>
                ) : (
                  <ErrorBoundary>
                    <AssistantMessage msg={msg} user={user} currentSessionId={currentSessionId} />
                  </ErrorBoundary>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div style={{ display: 'flex', alignItems: 'flex-start' }}>
              <div style={{
                padding: '14px 18px',
                borderRadius: '16px',
                borderBottomLeftRadius: '4px',
                backgroundColor: '#ffffff',
                border: '1px solid var(--border-color)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: 'var(--text-muted)'
              }}>
                <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                <span style={{ fontSize: '13px' }}>Assistant is thinking...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{padding: 'var(--space-4) var(--space-5)', borderTop: '1px solid var(--border-color)', backgroundColor: 'var(--bg-color)', flexShrink: 0}}>
          {!isSessionActive ? (
            <div style={{textAlign: 'center', color: 'var(--danger-color)', padding: '10px', fontSize: '13px', fontWeight: 500}}>
              Your Agent session is inactive. Agent operations are unavailable.
            </div>
          ) : (
            <form onSubmit={handleSend} style={{display: 'flex', gap: '10px', alignItems: 'flex-end'}}>
              <div style={{ flex: 1, position: 'relative' }}>
                <textarea
                  className="form-control"
                  style={{ 
                    width: '100%', 
                    resize: 'none', 
                    height: '52px',
                    padding: '15px 16px',
                    borderRadius: 'var(--radius-lg)',
                    lineHeight: '1.4'
                  }}
                  placeholder="Ask the CRM Agent anything..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend(e);
                    }
                  }}
                  disabled={loading}
                />
              </div>
              <button 
                type="submit" 
                className="btn btn-primary" 
                style={{ height: '52px', padding: '0 20px', borderRadius: 'var(--radius-lg)' }}
                disabled={loading || !prompt.trim()}
              >
                {loading ? <span className="spinner" style={{width: '18px', height: '18px', borderWidth: '2px', borderTopColor: 'transparent'}}></span> : <Send size={18} />}
                <span style={{ marginLeft: '8px' }}>Send</span>
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default AiAssistant;

