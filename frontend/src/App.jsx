import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
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
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import './index.css';

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
              <Route path="/customers" element={<Customers />} />
              <Route path="/ai-assistant" element={<AiAssistant />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Route>

            {/* Routes for MANAGER and STAFF */}
            <Route element={<ProtectedRoute allowedRoles={['MANAGER', 'STAFF']} />}>
              <Route path="/dashboard" element={<UserDashboard />} />
            </Route>

            {/* Admin Only Routes */}
            <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
              <Route path="/admin" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<AdminDashboard />} />
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

