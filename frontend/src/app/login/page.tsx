"use client";

import { useState } from 'react';
import { ShieldAlert, Lock, Mail, Loader2 } from 'lucide-react';
import { setAccessToken } from '@/lib/auth';
import { useAuth } from '@/context/AuthContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const { access_token } = await response.json();
        setAccessToken(access_token);
        await login(access_token);
      } else {
        const data = await response.json();
        setError(data.detail || 'Authentication failed');
      }
    } catch (err) {
      setError('Connection to security gateway failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#05070a] flex items-center justify-center p-4">
      <div className="w-full max-w-md animate-in fade-in zoom-in duration-500">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center mx-auto mb-4 shadow-2xl shadow-blue-500/20">
            <ShieldAlert className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Access Control</h1>
          <p className="text-slate-400 mt-2">Sign in to the AI Security Intelligence Hub</p>
        </div>

        <div className="glass p-8 rounded-3xl border border-slate-700/50 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Personnel Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input 
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-900/50 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                  placeholder="name@organization.com"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Secure Passkey</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                <input 
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-900/50 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {error && (
              <div className="bg-rose-500/10 border border-rose-500/50 text-rose-400 p-3 rounded-lg text-sm text-center">
                {error}
              </div>
            )}

            <button 
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-blue-600/20 active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Authenticate Access'}
            </button>
          </form>
        </div>

        <p className="text-center text-slate-500 text-xs mt-8">
          Authorized personnel only. All access attempts are monitored and logged.
        </p>
      </div>
    </div>
  );
}
