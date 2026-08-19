import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const Customers = () => {
  const { token } = useContext(AuthContext);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 10;
  
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/crm/customers?page=${page}&page_size=${pageSize}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setCustomers(data.items);
        setTotal(data.total);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchCustomers();
  }, [page, token]);

  return (
    <div>
      <div className="panel">
        <div className="panel-header">
          <h3>CRM Customers</h3>
          <div>
            <button className="btn btn-outline" onClick={fetchCustomers}>Refresh</button>
          </div>
        </div>
        
        {loading ? (
          <p>Loading customers...</p>
        ) : (
          <>
            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Company</th>
                    <th>Designation</th>
                    <th>Email</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {customers.length === 0 ? (
                    <tr><td colSpan="6">No customers found.</td></tr>
                  ) : (
                    customers.map(c => (
                      <tr key={c.id}>
                        <td>{c.customer_id}</td>
                        <td>{c.first_name} {c.last_name}</td>
                        <td>{c.company || '—'}</td>
                        <td>{c.designation || '—'}</td>
                        <td>{c.email}</td>
                        <td>
                          <button className="btn btn-outline btn-sm">View Details</button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            
            <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '20px', alignItems: 'center'}}>
              <span style={{fontSize: '0.85rem', color: 'var(--text-muted)'}}>
                Showing {customers.length} of {total} customers
              </span>
              <div>
                <button 
                  className="btn btn-outline btn-sm" 
                  disabled={page === 1} 
                  onClick={() => setPage(page - 1)}>
                  Previous
                </button>
                <button 
                  className="btn btn-outline btn-sm" 
                  disabled={page * pageSize >= total} 
                  onClick={() => setPage(page + 1)}>
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Customers;
