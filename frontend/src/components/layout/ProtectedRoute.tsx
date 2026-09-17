import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Role } from '../../types';

interface ProtectedRouteProps {
  allowedRoles?: Role[];
  roles?: Role[];
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles, roles, children }) => {
  const { isAuthenticated, role } = useAuth();
  const activeAllowed = allowedRoles || roles;

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (activeAllowed && role && !activeAllowed.includes(role)) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-slate-800 border border-slate-700 rounded-2xl p-8 text-center shadow-xl">
          <div className="w-12 h-12 rounded-full bg-red-500/10 text-red-500 flex items-center justify-center mx-auto mb-4 font-bold text-xl">
            403
          </div>
          <h2 className="text-xl font-bold mb-2">Access Restricted</h2>
          <p className="text-sm text-slate-400 mb-6">
            Your account role (<span className="text-blue-400 font-semibold">{role}</span>) does not have authorization to view this page.
          </p>
          <button
            onClick={() => window.location.href = '/'}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-xl text-xs transition-colors"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
