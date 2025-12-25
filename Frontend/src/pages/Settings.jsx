import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import { FaUser, FaGlobe, FaBell, FaShieldAlt, FaSignOutAlt, FaTrash } from 'react-icons/fa';

const Settings = () => {
    const [activeSection, setActiveSection] = useState('profile');
    const [language, setLanguage] = useState('English');
    const [reduceMotion, setReduceMotion] = useState(false);
    const [emailNotifications, setEmailNotifications] = useState(true);

    const renderContent = () => {
        switch (activeSection) {
            case 'profile':
                return (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold text-white mb-6">Profile Settings</h2>

                        <div className="flex items-center gap-6 mb-8">
                            <div className="w-24 h-24 rounded-full bg-orange-500/20 flex items-center justify-center border-2 border-orange-500/50">
                                <span className="text-4xl">👨‍🚀</span>
                            </div>
                            <div>
                                <h3 className="text-xl font-bold text-white">Vasco da Gama</h3>
                                <p className="text-gray-400">Explorer & Student</p>
                                <button className="mt-2 text-sm text-orange-400 hover:text-orange-300 font-medium">Change Avatar</button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-orange-200 text-xs font-bold uppercase tracking-wider">Full Name</label>
                                <input type="text" defaultValue="Vasco da Gama" className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:border-orange-500 focus:outline-none transition-colors" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-orange-200 text-xs font-bold uppercase tracking-wider">Email Address</label>
                                <input type="email" defaultValue="vasco@gurukul.app" className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:border-orange-500 focus:outline-none transition-colors" />
                            </div>
                            <div className="col-span-1 md:col-span-2 space-y-2">
                                <label className="text-orange-200 text-xs font-bold uppercase tracking-wider">Bio</label>
                                <textarea rows="4" defaultValue="Navigating the seas of knowledge." className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:border-orange-500 focus:outline-none transition-colors resize-none"></textarea>
                            </div>
                        </div>
                    </div>
                );
            case 'preferences':
                return (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold text-white mb-6">App Preferences</h2>

                        <div className="space-y-4">
                            <div className="bg-black/60 p-4 rounded-xl border border-white/10 flex justify-between items-center">
                                <div>
                                    <h3 className="text-white font-medium">Language</h3>
                                    <p className="text-gray-400 text-sm">Select your preferred language</p>
                                </div>
                                <select
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value)}
                                    className="bg-white/5 border border-white/10 text-white rounded-lg p-2 outline-none focus:border-orange-500"
                                >
                                    <option value="English">English</option>
                                    <option value="Hindi">Hindi (हिंदी)</option>
                                    <option value="Sanskrit">Sanskrit (संस्कृत)</option>
                                </select>
                            </div>

                            <div className="bg-black/60 p-4 rounded-xl border border-white/10 flex justify-between items-center">
                                <div>
                                    <h3 className="text-white font-medium">Reduce Motion</h3>
                                    <p className="text-gray-400 text-sm">Minimize animations for better accessibility</p>
                                </div>
                                <div
                                    className={`w-12 h-6 rounded-full p-1 cursor-pointer transition-colors duration-300 ${reduceMotion ? 'bg-orange-500' : 'bg-gray-600'}`}
                                    onClick={() => setReduceMotion(!reduceMotion)}
                                >
                                    <div className={`w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-300 ${reduceMotion ? 'translate-x-6' : 'translate-x-0'}`}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                );
            case 'notifications':
                return (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold text-white mb-6">Notifications</h2>
                        <div className="bg-black/60 p-4 rounded-xl border border-white/10 flex justify-between items-center">
                            <div>
                                <h3 className="text-white font-medium">Email Notifications</h3>
                                <p className="text-gray-400 text-sm">Receive study summaries and goal updates</p>
                            </div>
                            <div
                                className={`w-12 h-6 rounded-full p-1 cursor-pointer transition-colors duration-300 ${emailNotifications ? 'bg-orange-500' : 'bg-gray-600'}`}
                                onClick={() => setEmailNotifications(!emailNotifications)}
                            >
                                <div className={`w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-300 ${emailNotifications ? 'translate-x-6' : 'translate-x-0'}`}></div>
                            </div>
                        </div>
                    </div>
                );
            case 'security':
                return (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold text-white mb-6">Security & Account</h2>

                        <div className="space-y-4">
                            <button className="w-full flex items-center justify-between p-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded-xl transition-all group">
                                <span className="text-red-400 font-medium group-hover:text-red-300">Sign Out</span>
                                <FaSignOutAlt className="text-red-400 group-hover:text-red-300" />
                            </button>
                            <button className="w-full flex items-center justify-between p-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded-xl transition-all group">
                                <div>
                                    <p className="text-left text-red-400 font-medium group-hover:text-red-300">Delete Account</p>
                                    <p className="text-left text-red-500/60 text-xs">This action is irreversible</p>
                                </div>
                                <FaTrash className="text-red-400 group-hover:text-red-300" />
                            </button>
                        </div>
                    </div>
                );
            default:
                return null;
        }
    };

    const navItems = [
        { id: 'profile', icon: FaUser, label: 'Profile' },
        { id: 'preferences', icon: FaGlobe, label: 'Preferences' },
        { id: 'notifications', icon: FaBell, label: 'Notifications' },
        { id: 'security', icon: FaShieldAlt, label: 'Security' },
    ];

    return (
        <div className="flex pt-24 min-h-screen container mx-auto px-4 gap-6">
            <Sidebar />

            <main className="flex-grow flex gap-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                {/* Navigation Panel */}
                <div className="w-64 glass-panel no-hover p-6 rounded-3xl border border-white/10 h-fit">
                    <h1 className="text-2xl font-bold text-white mb-8 px-2">Settings</h1>
                    <div className="space-y-2">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => setActiveSection(item.id)}
                                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${activeSection === item.id
                                    ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/20'
                                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                                    }`}
                            >
                                <item.icon />
                                {item.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Content Panel */}
                <div className="flex-grow glass-panel no-hover p-8 rounded-3xl border border-white/10 relative overflow-hidden h-[calc(100vh-140px)] overflow-y-auto custom-scrollbar">
                    {/* Decorative Elements */}
                    <div className="absolute top-0 right-0 w-96 h-96 bg-orange-500/5 rounded-full blur-3xl pointer-events-none -translate-y-1/2 translate-x-1/2"></div>

                    <div className="relative z-10 max-w-2xl">
                        {renderContent()}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Settings;
