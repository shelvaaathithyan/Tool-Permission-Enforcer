import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import AiAssistant from '../pages/AiAssistant';
import { AuthContext } from '../context/AuthContext';
import AssistantMessage from '../components/assistant/AssistantMessage';
import ErrorBoundary from '../components/ErrorBoundary';

const mockUser = { id: 'u1', name: 'Test User', agent: { name: 'Test Agent', agent_id: 'A1' } };

const renderWithAuth = (ui) => {
  return render(
    <AuthContext.Provider value={{ user: mockUser, token: 'fake-token' }}>
      {ui}
    </AuthContext.Provider>
  );
};

// Silence console.error for expected test errors
const originalError = console.error;
beforeEach(() => {
  console.error = vi.fn();
  window.sessionStorage.clear();
  global.fetch = vi.fn();
  HTMLElement.prototype.scrollIntoView = vi.fn();
});
afterEach(() => {
  console.error = originalError;
  vi.restoreAllMocks();
});

describe('AiAssistant Component Robustness', () => {
  
  const setupFetchMock = (mockResponseData, ok = true) => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/auth/session')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ status: 'ACTIVE', session_id: 'S1' })
        });
      }
      if (url.includes('/agent/invoke')) {
        return Promise.resolve({
          ok,
          json: async () => mockResponseData
        });
      }
      return Promise.reject(new Error('not mocked'));
    });
  };

  const sendMessage = async (text) => {
    const input = screen.getByPlaceholderText(/ask the crm agent/i);
    const button = screen.getByRole('button', { name: /send/i });
    fireEvent.change(input, { target: { value: text } });
    fireEvent.click(button);
  };

  it('renders normal READ response (customer card)', async () => {
    setupFetchMock({
      response: 'Found customer',
      status: 'ALLOWED',
      decision: 'ALLOWED',
      tool_request: { tool_name: 'get_customer', operation: 'READ', resource: 'CUSTOMER', arguments: {} },
      result: { customer_id: 'CUST-1', first_name: 'Priya', last_name: 'S' }
    });
    
    renderWithAuth(<AiAssistant />);
    await waitFor(() => expect(screen.getByText(/ACTIVE/i)).toBeInTheDocument());
    await sendMessage('Get details');
    
    await waitFor(() => {
      expect(screen.getByText('✓ Customer Details')).toBeInTheDocument();
      expect(screen.getByText('Priya S')).toBeInTheDocument();
    });
  });

  it('renders array search response (search cards)', async () => {
    setupFetchMock({
      status: 'ALLOWED',
      decision: 'ALLOWED',
      tool_request: { tool_name: 'search_customers', operation: 'READ', resource: 'CUSTOMER', arguments: {} },
      result: [{ customer_id: 'CUST-2', first_name: 'Naren', last_name: 'G' }, { customer_id: 'CUST-3', first_name: 'Vikram', last_name: 'S' }]
    });
    
    renderWithAuth(<AiAssistant />);
    await waitFor(() => expect(screen.getByText(/ACTIVE/i)).toBeInTheDocument());
    await sendMessage('Search');
    
    await waitFor(() => {
      expect(screen.getByText('🔍 Customer Search')).toBeInTheDocument();
      expect(screen.getByText('Naren G')).toBeInTheDocument();
      expect(screen.getByText('Vikram S')).toBeInTheDocument();
    });
  });

  it('handles null result securely', async () => {
    setupFetchMock({
      status: 'ALLOWED',
      decision: 'ALLOWED',
      tool_request: { tool_name: 'get_customer', operation: 'READ', resource: 'CUSTOMER', arguments: {} },
      result: null
    });
    
    renderWithAuth(<AiAssistant />);
    await waitFor(() => expect(screen.getByText(/ACTIVE/i)).toBeInTheDocument());
    await sendMessage('Get missing');
    
    await waitFor(() => {
      expect(screen.getByText('✕ Customer Not Found')).toBeInTheDocument();
    });
  });

  it('handles string result safely without crashing', async () => {
    setupFetchMock({
      status: 'ALLOWED',
      decision: 'ALLOWED',
      tool_request: { tool_name: 'get_customer', operation: 'READ', resource: 'CUSTOMER', arguments: {} },
      result: "Just a string response"
    });
    
    renderWithAuth(<AiAssistant />);
    await waitFor(() => expect(screen.getByText(/ACTIVE/i)).toBeInTheDocument());
    await sendMessage('Get string');
    
    await waitFor(() => {
      expect(screen.queryByText('✓ Customer Details')).not.toBeInTheDocument();
      // It falls back to unsupported or general because the string is not a customer object
    });
    expect(screen.getByText(/I processed your request/i)).toBeInTheDocument();
  });

  it('handles object result safely', async () => {
    setupFetchMock({
      status: 'ALLOWED',
      decision: 'ALLOWED',
      tool_request: { tool_name: 'search_customers', operation: 'READ', resource: 'CUSTOMER', arguments: {} },
      result: { total: 0, items: [] }
    });
    
    renderWithAuth(<AiAssistant />);
    await waitFor(() => expect(screen.getByText(/ACTIVE/i)).toBeInTheDocument());
    await sendMessage('Get object');
    
    await waitFor(() => {
      expect(screen.getByText('✕ Customer Not Found')).toBeInTheDocument();
    });
  });

  it('handles malformed JSON response safely', async () => {
    global.fetch.mockImplementation((url) => {
      if (url.includes('/auth/session')) {
        return Promise.resolve({ ok: true, json: async () => ({ status: 'ACTIVE', session_id: 'S1' }) });
      }
      if (url.includes('/agent/invoke')) {
        return Promise.resolve({ ok: true, json: async () => { throw new Error('Bad JSON'); } });
      }
      return Promise.reject(new Error('not mocked'));
    });
      
    renderWithAuth(<AiAssistant />);
    await waitFor(() => expect(screen.getByText(/ACTIVE/i)).toBeInTheDocument());
    await sendMessage('malformed');
    
    await waitFor(() => {
      expect(screen.getByText('⚠ Assistant Error')).toBeInTheDocument();
    });
  });

  it('handles unsupported prompt (no tool request)', async () => {
    setupFetchMock({
      status: 'ALLOWED',
      decision: 'ALLOWED',
      tool_request: null,
      result: null
    });
    
    renderWithAuth(<AiAssistant />);
    await waitFor(() => expect(screen.getByText(/ACTIVE/i)).toBeInTheDocument());
    await sendMessage('Unsupported prompt');
    
    await waitFor(() => {
      expect(screen.getByText('ℹ Unsupported Request')).toBeInTheDocument();
    });
  });

  it('ignores corrupted sessionStorage safely', () => {
    sessionStorage.setItem(`crm_agent_chat_${mockUser.id}`, 'bad-json-data');
    renderWithAuth(<AiAssistant />);
    // Should not crash, renders empty state
    expect(screen.getByText(/How can I help you today?/i)).toBeInTheDocument();
  });

  it('renders ErrorBoundary when AssistantMessage throws', async () => {
    // We intentionally create a component that throws
    const ThrowingComponent = () => {
      throw new Error("Simulated rendering error");
    };
    
    render(
      <ErrorBoundary>
        <ThrowingComponent />
      </ErrorBoundary>
    );

    await waitFor(() => {
      expect(screen.getByText(/Something went wrong while displaying this response/i)).toBeInTheDocument();
    });
  });
});
