import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { useContext } from 'react';
import { ProtectedRoute } from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Signup from './pages/Signup';
import UserDashboard from './pages/UserDashboard';
import AdminDashboard from './pages/AdminDashboard';
import Customers from './pages/Customers';
import AiAssistant from './pages/AiAssistant';
import SignupRequests from './pages/SignupRequests';
import Users from './pages/Users';
import Agents from './pages/Agents';
import AuditLogs from './pages/AuditLogs';
import SecurityAlerts from './pages/SecurityAlerts';

import Settings from './pages/Settings';
import './index.css';

const DashboardRouter = () => {
  const { user } = useContext(AuthContext);
  if (user?.role === 'ADMIN') {
    return <AdminDashboard />;
  }
  return <UserDashboard />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          
          <Route element={<Layout />}>
            {/* Routes for All Authenticated Users */}
            <Route element={<ProtectedRoute allowedRoles={['ADMIN', 'MANAGER', 'STAFF']} />}>
              <Route path="/dashboard" element={<DashboardRouter />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/ai-assistant" element={<AiAssistant />} />

              <Route path="/settings" element={<Settings />} />
            </Route>

            {/* Admin Only Routes */}
            <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
              <Route path="/admin" element={<Navigate to="/dashboard" replace />} />
              <Route path="/signup-requests" element={<SignupRequests />} />
              <Route path="/users" element={<Users />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/audit-logs" element={<AuditLogs />} />
              <Route path="/security-alerts" element={<SecurityAlerts />} />
            </Route>
          </Route>

          {/* Catch all redirect */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

