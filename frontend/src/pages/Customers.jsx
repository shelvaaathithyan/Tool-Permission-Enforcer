import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const Customers = () => {
  const { token } = useContext(AuthContext);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 100;
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [saving, setSaving] = useState(false);
  
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

  const openEditModal = (customer) => {
    setEditingCustomer({ ...customer });
    setIsModalOpen(true);
  };

  const closeEditModal = () => {
    setIsModalOpen(false);
    setEditingCustomer(null);
  };

  const handleEditChange = (e) => {
    const { name, value, type, checked } = e.target;
    if (type === 'checkbox' && name === 'session_status') {
      setEditingCustomer({ ...editingCustomer, session_status: checked ? 'ACTIVE' : 'INACTIVE' });
    } else {
      setEditingCustomer({ ...editingCustomer, [name]: value });
    }
  };

  const handleSaveCustomer = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/crm/customers/${editingCustomer.customer_id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          first_name: editingCustomer.first_name,
          last_name: editingCustomer.last_name,
          email: editingCustomer.email,
          phone: editingCustomer.phone,
          company: editingCustomer.company,
          designation: editingCustomer.designation,
          session_status: editingCustomer.session_status
        })
      });
      
      if (res.ok) {
        // Refresh
        await fetchCustomers();
        closeEditModal();
        alert("Customer updated successfully");
      } else {
        const errData = await res.json();
        alert("Error: " + JSON.stringify(errData));
      }
    } catch (e) {
      console.error(e);
      alert("Error saving customer.");
    }
    setSaving(false);
  };

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
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {customers.length === 0 ? (
                    <tr><td colSpan="7">No customers found.</td></tr>
                  ) : (
                    customers.map(c => (
                      <tr key={c.id}>
                        <td>{c.customer_id}</td>
                        <td>{c.first_name} {c.last_name}</td>
                        <td>{c.company || '—'}</td>
                        <td>{c.designation || '—'}</td>
                        <td>{c.email}</td>
                        <td>
                          {c.session_status === 'ACTIVE' ? (
                            <span className="badge success">ACTIVE</span>
                          ) : (
                            <span className="badge danger">INACTIVE</span>
                          )}
                        </td>
                        <td>
                          <button 
                            className="btn btn-outline btn-sm" 
                            onClick={() => openEditModal(c)}>
                            Edit Details
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            
            <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '20px', alignItems: 'center'}}>
              <span style={{fontSize: '0.85rem', color: 'var(--text-muted)'}}>
                Showing {customers.length} customers
              </span>
            </div>
          </>
        )}
      </div>

      {isModalOpen && editingCustomer && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', 
          justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }}>
          <div className="panel" style={{width: '500px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto'}}>
            <div className="panel-header">
              <h3>Edit Customer: {editingCustomer.customer_id}</h3>
              <button className="btn btn-sm btn-outline" onClick={closeEditModal}>X</button>
            </div>
            <form onSubmit={handleSaveCustomer}>
              <div className="form-group">
                <label>First Name</label>
                <input type="text" name="first_name" className="form-control" value={editingCustomer.first_name || ''} onChange={handleEditChange} required />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input type="text" name="last_name" className="form-control" value={editingCustomer.last_name || ''} onChange={handleEditChange} required />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input type="email" name="email" className="form-control" value={editingCustomer.email || ''} onChange={handleEditChange} required />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input type="text" name="phone" className="form-control" value={editingCustomer.phone || ''} onChange={handleEditChange} />
              </div>
              <div className="form-group">
                <label>Company</label>
                <input type="text" name="company" className="form-control" value={editingCustomer.company || ''} onChange={handleEditChange} />
              </div>
              <div className="form-group">
                <label>Designation</label>
                <input type="text" name="designation" className="form-control" value={editingCustomer.designation || ''} onChange={handleEditChange} />
              </div>
              
              <div className="form-group" style={{marginTop: '20px', padding: '15px', border: '1px solid var(--border-color)', borderRadius: '4px'}}>
                <label style={{display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', margin: 0}}>
                  <input 
                    type="checkbox" 
                    name="session_status"
                    checked={editingCustomer.session_status === 'ACTIVE'}
                    onChange={handleEditChange}
                    style={{width: '20px', height: '20px'}}
                  />
                  <strong>Session Status: {editingCustomer.session_status === 'ACTIVE' ? 'Active' : 'Inactive'}</strong>
                </label>
                <p style={{fontSize: '0.8rem', color: 'var(--text-muted)', margin: '5px 0 0 0'}}>
                  Toggle this to simulate whether the CRM customer is active or inactive for AI operations.
                </p>
              </div>

              <div style={{display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px'}}>
                <button type="button" className="btn btn-outline" onClick={closeEditModal} disabled={saving}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Customers;
