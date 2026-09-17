import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, Role } from '../types';
import { authApi } from '../api/auth';

interface AuthContextType {
  token: string | null;
  user: User | null;
  role: Role | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function parseJwtPayload(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('secureExamToken'));
  const [user, setUser] = useState<User | null>(() => {
    const savedToken = localStorage.getItem('secureExamToken');
    if (!savedToken) return null;
    const payload = parseJwtPayload(savedToken);
    if (!payload) return null;
    return {
      id: Number(payload.sub),
      name: payload.name || `User #${payload.sub}`,
      email: payload.email || '',
      role: payload.role as Role,
    };
  });

  useEffect(() => {
    const handleUnauthorized = () => {
      logout();
    };
    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await authApi.login(email, password);
    const newToken = res.access_token;
    localStorage.setItem('secureExamToken', newToken);
    setToken(newToken);

    const payload = parseJwtPayload(newToken);
    if (payload) {
      setUser({
        id: Number(payload.sub),
        name: payload.name || email.split('@')[0],
        email: email,
        role: payload.role as Role,
      });
    }
  };

  const logout = () => {
    localStorage.removeItem('secureExamToken');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        role: user?.role || null,
        isAuthenticated: !!token && !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
