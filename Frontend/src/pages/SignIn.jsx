import React, { useState } from 'react';
import { FaArrowRight } from 'react-icons/fa';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { setUserRole } from '../utils/roles';
import API_BASE_URL from '../config';

const SignIn = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        
        try {
            const { user } = await login(email, password);
            
            // Gurukul is student-only, always redirect to student dashboard
            setUserRole('student');
            navigate('/dashboard');
        } catch (err) {
            console.error('Login error:', err);
            setError(err.message || 'Failed to sign in. Please check your credentials and try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-[calc(100vh-100px)] px-3 sm:px-4 py-4">
            {/* Login Card */}
            <div className="w-full max-w-md glass-panel p-5 sm:p-6 md:p-10 animate-fade-in-up border border-white/10 shadow-2xl relative overflow-hidden">

                {/* Subtle decorative glow */}
                <div className="absolute -top-10 -right-10 w-32 h-32 bg-accent/20 rounded-full blur-3xl"></div>
                <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-orange-900/40 rounded-full blur-3xl"></div>

                <div className="relative z-10">
                    <h2 className="text-3xl sm:text-4xl font-heading font-bold mb-2 text-center text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">Welcome Back</h2>
                    <p className="text-center text-gray-400 text-xs sm:text-sm mb-6 sm:mb-8 tracking-wide">Enter the Gurukul to continue your journey.</p>

                    {error && <div className="bg-red-500/20 text-red-300 p-3 rounded mb-4 text-sm border border-red-500/30 text-center">{error}</div>}

                    <form className="flex flex-col gap-5" onSubmit={handleSubmit}>
                        <div className="space-y-1">
                            <label className="text-xs font-semibold uppercase tracking-wider text-gray-400 ml-1">Email Address</label>
                            <input
                                type="email"
                                placeholder="student@gurukul.com"
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-accent/50 focus:bg-white/10 transition-all"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-semibold uppercase tracking-wider text-gray-400 ml-1">Password</label>
                            <input
                                type="password"
                                placeholder="••••••••"
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-accent/50 focus:bg-white/10 transition-all"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <button 
                            type="submit" 
                            disabled={loading}
                            className="w-full mt-2 py-3 rounded-lg bg-gradient-to-r from-orange-600 to-amber-700 hover:from-orange-500 hover:to-amber-600 text-white font-bold tracking-wide shadow-lg transform transition-all hover:-translate-y-1 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                        >
                            {loading ? 'Signing In...' : 'Sign In'} 
                            {!loading && <FaArrowRight className="text-sm opacity-80" />}
                        </button>
                    </form>

                    <p className="mt-8 text-center text-xs text-gray-400">
                        Not a scholar yet? <Link to="/signup" className="text-accent hover:text-orange-300 font-semibold transition-colors">Apply for Admission</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default SignIn;
