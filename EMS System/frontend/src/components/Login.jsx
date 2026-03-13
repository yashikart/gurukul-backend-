import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useDemo } from '../context/DemoContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { isDemoMode, toggleDemoMode } = useDemo();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (email.toLowerCase().endsWith('@demo.com') && !isDemoMode) {
      setError('This is a demo account. Please enable "DEMO MODE" below the login button to use these credentials.');
      setLoading(false);
      return;
    }

    const result = await login(email, password);

    if (result.success) {
      navigate('/dashboard');
    } else {
      let errorMessage = result.message;

      // Helpful hint for race conditions during startup/deployment
      if (isDemoMode && email.toLowerCase().endsWith('@demo.com') && (errorMessage.includes('Incorrect') || errorMessage.includes('401'))) {
        errorMessage = "Demo login failed. If the system was just restarted, please wait 3-5 seconds for initialization and try again.";
      }

      setError(errorMessage);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background gradient orbs */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-accent-green/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] rounded-full bg-accent-blue/5 blur-[120px] pointer-events-none" />

      <div className="max-w-md w-full animate-fade-in relative z-10">
        {/* Login Card — Glassmorphism */}
        <div className="bg-[#1A1A2E]/80 backdrop-blur-xl border border-[#2A2A3E] rounded-3xl p-8 shadow-2xl">
          <div className="text-center mb-8">
            <h1 className="heading-serif text-4xl mb-3 tracking-tight">
              Gurukul
            </h1>
            <p className="text-gray-400 text-sm">School Management System</p>
          </div>

          {error && (
            <div className="error-box mb-6">
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="input-dark"
                placeholder="Enter your email"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="input-dark"
                placeholder="Enter your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3.5 text-base mt-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="inline-block w-4 h-4 border-2 border-dark-bg/30 border-t-dark-bg rounded-full animate-spin" />
                  Logging in...
                </span>
              ) : 'Login'}
            </button>
          </form>

          {/* Demo Mode Toggle */}
          <div className="mt-8 pt-6 border-t border-[#2A2A3E] flex items-center justify-center gap-3">
            <span className={`text-xs font-bold uppercase tracking-wider ${isDemoMode ? 'text-accent-green' : 'text-gray-500'}`}>Demo Mode</span>
            <button
              onClick={toggleDemoMode}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-all duration-300 ${isDemoMode ? 'bg-accent-green' : 'bg-[#2A2A3E]'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-300 ${isDemoMode ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>

          <div className="mt-5 text-center">
            <p className="text-gray-500 text-xs">Login with your email and password. All user roles can login here.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
