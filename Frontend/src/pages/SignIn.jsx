import React from 'react';
import { FaArrowRight } from 'react-icons/fa';
import { Link } from 'react-router-dom';

const SignIn = () => {
    return (
        <div className="flex items-center justify-center min-h-[calc(100vh-100px)] px-4">
            {/* Login Card */}
            <div className="w-full max-w-md glass-panel p-10 animate-fade-in-up border border-white/10 shadow-2xl relative overflow-hidden">

                {/* Subtle decorative glow */}
                <div className="absolute -top-10 -right-10 w-32 h-32 bg-accent/20 rounded-full blur-3xl"></div>
                <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-orange-900/40 rounded-full blur-3xl"></div>

                <div className="relative z-10">
                    <h2 className="text-4xl font-heading font-bold mb-2 text-center text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400">Welcome Back</h2>
                    <p className="text-center text-gray-400 text-sm mb-8 tracking-wide">Enter the Gurukul to continue your journey.</p>

                    <form className="flex flex-col gap-5">
                        <div className="space-y-1">
                            <label className="text-xs font-semibold uppercase tracking-wider text-gray-400 ml-1">Email Address</label>
                            <input
                                type="email"
                                placeholder="student@gurukul.com"
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-accent/50 focus:bg-white/10 transition-all"
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-semibold uppercase tracking-wider text-gray-400 ml-1">Password</label>
                            <input
                                type="password"
                                placeholder="••••••••"
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-accent/50 focus:bg-white/10 transition-all"
                            />
                        </div>



                        <button className="w-full mt-2 py-3 rounded-lg bg-gradient-to-r from-orange-600 to-amber-700 hover:from-orange-500 hover:to-amber-600 text-white font-bold tracking-wide shadow-lg transform transition-all hover:-translate-y-1 flex items-center justify-center gap-2">
                            Sign In <FaArrowRight className="text-sm opacity-80" />
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
