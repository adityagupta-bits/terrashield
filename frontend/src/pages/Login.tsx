import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api/client';
import { useAuthStore } from '../../store/authStore';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const [email, setEmail] = useState('admin@terrashield.gov.in');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const res = await api.login(email, password);
      setAuth(res.token, res.role, res.email);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <div className="min-h-screen bg-[#070d12] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 sm:p-8 space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 text-2xl shadow-lg shadow-cyan-500/20">
            🛡️
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            TERRA SHIELD
          </h1>
          <p className="text-xs text-slate-400">
            National Disaster Response Force & Authority Command Portal
          </p>
        </div>

        {/* Error notification */}
        {error && (
          <div className="bg-rose-950/80 border border-rose-600 text-rose-200 text-xs p-3 rounded-lg font-mono">
            ⚠️ {error}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="text-xs text-slate-400 block mb-1 font-medium">Official Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white font-mono outline-none focus:border-cyan-500 transition-colors"
              placeholder="admin@terrashield.gov.in"
            />
          </div>

          <div>
            <label className="text-xs text-slate-400 block mb-1 font-medium">Security Credential / Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white font-mono outline-none focus:border-cyan-500 transition-colors"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-cyan-600 hover:bg-cyan-500 active:bg-cyan-700 disabled:opacity-50 text-white font-bold text-xs py-2.5 rounded-lg shadow-lg shadow-cyan-600/20 transition-all uppercase tracking-wider"
          >
            {isLoading ? 'Verifying Credentials...' : 'Authenticate & Enter Command Center'}
          </button>
        </form>

        {/* One-Click Demo Credentials Fill */}
        <div className="pt-2 border-t border-slate-800/80 space-y-2">
          <div className="text-[11px] text-slate-400 text-center font-mono">
            Demo Authority Access:
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickFill('admin@terrashield.gov.in', 'admin123')}
              className="bg-slate-800/60 hover:bg-slate-800 border border-slate-700 text-cyan-300 text-[11px] font-mono py-1.5 px-2 rounded text-center transition-colors"
            >
              👮 Authority (Admin)
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('viewer@terrashield.gov.in', 'viewer123')}
              className="bg-slate-800/60 hover:bg-slate-800 border border-slate-700 text-slate-300 text-[11px] font-mono py-1.5 px-2 rounded text-center transition-colors"
            >
              👁️ Observer (Viewer)
            </button>
          </div>
        </div>

        <div className="text-center pt-2">
          <a
            href="/citizen"
            className="text-xs text-slate-500 hover:text-cyan-400 transition-colors inline-flex items-center gap-1"
          >
            <span>Going to Citizen Emergency Advisory?</span>
            <span className="font-semibold text-cyan-400">Citizen Portal →</span>
          </a>
        </div>
      </div>
    </div>
  );
};
