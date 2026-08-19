import React, { useContext } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

export const ProtectedRoute = ({ allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useContext(AuthContext);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // If Admin tries to access User Dashboard, let them or redirect to Admin
    if (user.role === 'ADMIN') {
        return <Navigate to="/admin" replace />;
    }
    // If Manager/Staff tries to access Admin Dashboard
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};
