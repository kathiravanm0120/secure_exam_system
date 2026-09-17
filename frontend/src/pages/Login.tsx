import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Shield, Eye, EyeOff, Lock, AlertCircle } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRoleSelect = (roleEmail: string) => {
    setEmail(roleEmail);
    setPassword('password123');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Decorative Blur */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="flex justify-center">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center shadow-xl shadow-blue-500/30">
            <Shield className="w-7 h-7" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-black text-white tracking-tight">
          Secure Exam Control
        </h2>
        <p className="mt-1 text-center text-xs text-slate-400 font-medium">
          End-to-End CBT Integrity & Paper Leak Prevention Platform
        </p>
      </div>

      <div className="mt-7 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="bg-slate-900 border border-slate-800 py-8 px-7 shadow-2xl rounded-2xl sm:px-10">
          <form className="space-y-5" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-xl text-xs font-semibold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5">Email address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                placeholder="admin@example.com"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-800/80 border border-slate-700/80 rounded-xl px-3.5 py-2.5 pr-10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl text-xs shadow-lg shadow-blue-600/25 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Lock className="w-3.5 h-3.5" />
              <span>{isLoading ? 'Authenticating...' : 'Sign in to platform'}</span>
            </button>
          </form>

          {/* Quick Demo Role Selector */}
          <div className="mt-6 pt-5 border-t border-slate-800">
            <span className="block text-[11px] font-bold text-slate-400 mb-2">Quick Sign-in Roles (Demo):</span>
            <div className="grid grid-cols-2 gap-1.5 text-[11px]">
              <button
                type="button"
                onClick={() => handleRoleSelect('admin@example.com')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 p-2 rounded-lg text-left font-medium border border-slate-700/50"
              >
                👑 Admin
              </button>
              <button
                type="button"
                onClick={() => handleRoleSelect('setter_a@example.com')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 p-2 rounded-lg text-left font-medium border border-slate-700/50"
              >
                ✏️ Setter
              </button>
              <button
                type="button"
                onClick={() => handleRoleSelect('reviewer_a@example.com')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 p-2 rounded-lg text-left font-medium border border-slate-700/50"
              >
                🔍 Reviewer
              </button>
              <button
                type="button"
                onClick={() => handleRoleSelect('candidate_a@example.com')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 p-2 rounded-lg text-left font-medium border border-slate-700/50"
              >
                🎓 Candidate
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
