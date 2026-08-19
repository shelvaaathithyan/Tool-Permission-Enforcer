import React, { useState } from 'react';

const isArrayResult = (val) => Array.isArray(val) || (val && Array.isArray(val.items));
const getArrayResult = (val) => Array.isArray(val) ? val : (val && Array.isArray(val.items) ? val.items : []);
const isCustomerObject = (val) => val && typeof val === 'object' && !Array.isArray(val) && val.customer_id;
const isObjectResult = (val) => val && typeof val === 'object' && !Array.isArray(val);

const normalizeMessage = (msg, user, currentSessionId) => {
  const { toolRequest, status, decision, reason, result, text } = msg;
  const safeToolRequest = toolRequest || {};
  const { operation, resource, tool_name: tool, arguments: args = {} } = safeToolRequest;
  
  const agent = user?.agent?.name || 'Unknown Agent';
  const sessionId = msg.sessionId || currentSessionId || '—';
  const effectiveDecision = decision || status;

  let type = "unsupported";
  
  if (status === "ERROR") {
    type = "error";
  } else if (safeToolRequest && tool) {
    if (effectiveDecision === "BLOCKED") {
      if (reason && reason.includes("INACTIVE")) {
        type = "inactive";
      } else if (reason && reason.includes("not be found")) {
        type = "not_found";
      } else {
        type = "blocked";
      }
    } else if (effectiveDecision === "ALLOWED") {
       if (!result || result.error) {
         type = "not_found";
       } else if (isArrayResult(result)) {
         const arr = getArrayResult(result);
         if (arr.length === 0) {
           type = "not_found";
         } else if (arr.length === 1 && isCustomerObject(arr[0])) {
           type = "customer";
         } else {
           type = "search";
         }
       } else if (isCustomerObject(result)) {
         type = "customer";
       } else if (isObjectResult(result)) {
         // Some other object, maybe single search result not matching customerObject strictly?
         type = "customer"; 
       } else {
         type = "general";
       }
    }
  }

  // Ensure toolRequest is safely handled even when not supported
  const safeOperation = operation || 'NONE';
  const safeTool = tool || 'NONE';
  const safeResource = resource || 'NONE';

  return {
    type, decision: effectiveDecision, operation: safeOperation, tool: safeTool, resource: safeResource,
    customer: type === "customer" ? (isArrayResult(result) ? getArrayResult(result)[0] : result) : null,
    customers: type === "search" ? getArrayResult(result) : null,
    agent, sessionId, reason, result, args, text
  };
};

const AssistantMessage = ({ msg, user, currentSessionId }) => {
  const data = normalizeMessage(msg, user, currentSessionId);
  const [showDetails, setShowDetails] = useState(false);
  const [showArgs, setShowArgs] = useState(false);

  const renderDetails = () => (
    <div style={{marginTop: '15px', borderTop: '1px solid var(--border-color)', paddingTop: '10px'}}>
      <div 
        style={{color: 'var(--primary-color)', cursor: 'pointer', fontSize: '0.9rem', userSelect: 'none'}}
        onClick={() => setShowDetails(!showDetails)}
      >
        View operation details {showDetails ? '▴' : '▾'}
      </div>
      
      {showDetails && (
        <div style={{marginTop: '10px', fontSize: '0.85rem', backgroundColor: 'rgba(0,0,0,0.02)', padding: '10px', borderRadius: '4px'}}>
          <div style={{marginBottom: '5px'}}><strong>Operation:</strong> {data.operation}</div>
          <div style={{marginBottom: '5px'}}><strong>Resource:</strong> {data.resource}</div>
          <div style={{marginBottom: '5px'}}><strong>Tool:</strong> {data.tool}</div>
          <div style={{marginBottom: '5px'}}><strong>Agent:</strong> {data.agent}</div>
          <div style={{marginBottom: '5px'}}><strong>Session:</strong> {data.sessionId}</div>
          <div style={{marginBottom: '5px'}}>
            <strong>Decision:</strong>{' '}
            <span style={{color: data.decision === 'ALLOWED' ? 'var(--success-color)' : 'var(--danger-color)', fontWeight: 'bold'}}>
              {data.decision}
            </span>
          </div>
          {data.reason && <div style={{marginBottom: '5px'}}><strong>Reason:</strong> {data.reason}</div>}
          
          {data.args && Object.keys(data.args).length > 0 && (
            <div style={{marginTop: '10px', borderTop: '1px dashed #ccc', paddingTop: '10px'}}>
              <div 
                style={{color: 'var(--primary-color)', cursor: 'pointer', fontSize: '0.85rem', userSelect: 'none'}}
                onClick={() => setShowArgs(!showArgs)}
              >
                View raw tool arguments {showArgs ? '▴' : '▾'}
              </div>
              {showArgs && (
                <pre style={{margin: '5px 0 0 0', backgroundColor: '#f4f4f4', padding: '10px', borderRadius: '4px', fontSize: '0.8rem'}}>
                  {JSON.stringify(data.args, null, 2)}
                </pre>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );

  const cardStyle = {
    backgroundColor: '#fff',
    border: '1px solid var(--border-color)',
    borderRadius: '8px',
    padding: '15px',
    marginTop: '10px',
    color: 'var(--text-color)',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
  };

  const headerStyle = (color) => ({
    display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '600', fontSize: '1.1rem', color, marginBottom: '10px'
  });

  if (data.type === 'general') {
    return (
      <div>
        <div style={{whiteSpace: 'pre-wrap', lineHeight: '1.5'}}>{data.text}</div>
        {data.tool !== 'NONE' && renderDetails()}
      </div>
    );
  }

  if (data.type === 'unsupported') {
    return (
      <div style={{...cardStyle, borderLeft: '4px solid #6c757d'}}>
        <div style={headerStyle('#6c757d')}>ℹ Unsupported Request</div>
        <p style={{margin: '0 0 10px 0'}}>I couldn't process that request.</p>
        <p style={{margin: 0, color: 'var(--text-muted)'}}>Please try asking about a CRM customer or supported CRM operation.</p>
        {data.tool !== 'NONE' && renderDetails()}
      </div>
    );
  }

  if (data.type === 'error') {
    return (
      <div style={{...cardStyle, borderLeft: '4px solid var(--danger-color)'}}>
        <div style={headerStyle('var(--danger-color)')}>⚠ Assistant Error</div>
        <p style={{margin: 0}}>I couldn't complete the request right now.</p>
        <p style={{margin: '5px 0 0 0', color: 'var(--text-muted)'}}>Please try again.</p>
      </div>
    );
  }

  if (data.type === 'customer') {
    const c = data.customer;
    return (
      <div style={cardStyle}>
        <div style={headerStyle('var(--success-color)')}>✓ Customer Details</div>
        <div style={{marginBottom: '10px'}}>
          <div style={{fontWeight: 'bold', fontSize: '1.1rem'}}>{c.first_name} {c.last_name}</div>
          <div style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>{c.customer_id}</div>
        </div>
        <div style={{fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '4px'}}>
          <div><strong>Company:</strong> {c.company}</div>
          <div><strong>Designation:</strong> {c.designation}</div>
          <div><strong>Email:</strong> {c.email}</div>
          <div><strong>Status:</strong> <span className={`badge ${c.session_status === 'ACTIVE' ? 'success' : 'secondary'}`}>{c.session_status}</span></div>
        </div>
        {renderDetails()}
      </div>
    );
  }

  if (data.type === 'search') {
    const list = Array.isArray(data.customers) ? data.customers : [];
    
    if (list.length === 0) {
      return (
        <div style={{...cardStyle, borderLeft: '4px solid var(--danger-color)'}}>
          <div style={headerStyle('var(--danger-color)')}>✕ Customer Not Found</div>
          <p style={{margin: '0 0 10px 0'}}>No matching customers were found in the CRM.</p>
          {renderDetails()}
        </div>
      );
    }
    
    return (
      <div style={cardStyle}>
        <div style={headerStyle('var(--primary-color)')}>🔍 Customer Search</div>
        <div style={{marginBottom: '15px', color: 'var(--text-muted)'}}>Found {list.length} customers</div>
        
        <div style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
          {list.map((c, i) => (
            <div key={i} style={{border: '1px solid #eee', padding: '10px', borderRadius: '4px'}}>
              <div style={{fontWeight: 'bold'}}>{c?.first_name || 'Unknown'} {c?.last_name || ''}</div>
              <div style={{color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: '5px'}}>{c?.customer_id || '—'}</div>
              <div style={{fontSize: '0.85rem'}}>{c?.designation || '—'}</div>
              <div style={{fontSize: '0.85rem'}}>{c?.company || '—'}</div>
              <div style={{marginTop: '5px'}}>
                <span className={`badge ${c?.session_status === 'ACTIVE' ? 'success' : 'secondary'}`} style={{fontSize: '0.7rem'}}>
                  Status: {c?.session_status || 'UNKNOWN'}
                </span>
              </div>
            </div>
          ))}
        </div>
        {renderDetails()}
      </div>
    );
  }

  if (data.type === 'blocked') {
    return (
      <div style={{...cardStyle, borderLeft: '4px solid var(--danger-color)'}}>
        <div style={headerStyle('var(--danger-color)')}>✕ Operation Blocked</div>
        <p style={{margin: '0 0 10px 0'}}>{data.text}</p>
        <p style={{margin: '0 0 10px 0', color: 'var(--danger-color)', fontWeight: '500'}}>No changes were made to the CRM.</p>
        {renderDetails()}
      </div>
    );
  }

  if (data.type === 'inactive') {
    const searchName = data.args?.customer_id || "the requested customer";
    return (
      <div style={{...cardStyle, borderLeft: '4px solid #fd7e14'}}>
        <div style={headerStyle('#fd7e14')}>⚠ Customer Unavailable</div>
        <div style={{marginBottom: '10px'}}>
          <div style={{fontWeight: 'bold', fontSize: '1.1rem'}}>{searchName}</div>
        </div>
        <div style={{marginBottom: '10px'}}>
          <strong>Status:</strong> <span className="badge secondary">INACTIVE</span>
        </div>
        <p style={{margin: '0 0 10px 0'}}>The customer's session is inactive, so the requested information cannot be accessed.</p>
        <p style={{margin: '0 0 10px 0', color: 'var(--text-muted)'}}>No customer data was returned.</p>
        {renderDetails()}
      </div>
    );
  }

  if (data.type === 'not_found') {
    const searchName = data.args?.customer_id || data.args?.company || data.args?.query || data.args?.designation || "the requested customer";
    return (
      <div style={{...cardStyle, borderLeft: '4px solid var(--danger-color)'}}>
        <div style={headerStyle('var(--danger-color)')}>✕ Customer Not Found</div>
        <p style={{margin: '0 0 10px 0'}}>I couldn't find "{searchName}" in the CRM.</p>
        <p style={{margin: '0 0 10px 0', color: 'var(--text-muted)'}}>No changes were made.</p>
        {renderDetails()}
      </div>
    );
  }

  return <div>{data.text}</div>;
};

export default AssistantMessage;
