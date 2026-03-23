"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getAccessToken, fetchWithAuth, removeAccessToken } from '@/lib/auth';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  role: 'admin' | 'analyst' | 'executive';
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const loadUser = async () => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetchWithAuth('http://localhost:8000/api/v1/auth/me');
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        removeAccessToken();
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUser();
  }, []);

  const login = async (token: string) => {
    setLoading(true);
    await loadUser();
    router.push('/');
  };

  const logout = () => {
    removeAccessToken();
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
