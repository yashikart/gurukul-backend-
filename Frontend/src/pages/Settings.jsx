import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { FaUser, FaGlobe, FaBell, FaShieldAlt, FaSignOutAlt, FaTrash } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../supabaseClient';
import { useModal } from '../contexts/ModalContext';
import { setLanguage, getCurrentLanguage } from '../utils/languageSupport';
import { getCurrentRole, setUserRole, getRoleDisplayName, ROLES, getDashboardPath } from '../utils/roles';
import { useNavigate } from 'react-router-dom';

const Settings = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const { confirm, prompt, alert } = useModal();
    const [activeSection, setActiveSection] = useState('profile');
    const [userRole, setUserRoleState] = useState(() => getCurrentRole());
    
    // Profile state with localStorage persistence
    const [fullName, setFullName] = useState(() => {
        const saved = localStorage.getItem('user_fullName');
        return saved || (user?.email ? user.email.split('@')[0] : 'Vasco da Gama');
    });
    const [email, setEmail] = useState(() => {
        const saved = localStorage.getItem('user_email');
        return saved || (user?.email || 'vasco@gurukul.app');
    });
    const [bio, setBio] = useState(() => {
        const saved = localStorage.getItem('user_bio');
        return saved || 'Navigating the seas of knowledge.';
    });
    
    // Preferences state with localStorage persistence
    const [language, setLanguageState] = useState(() => {
        const saved = getCurrentLanguage();
        // Map language codes to display names
        const langMap = { 'en': 'English', 'ar': 'Arabic', 'he': 'Hebrew', 'ur': 'Urdu', 'fa': 'Persian' };
        return langMap[saved] || 'English';
    });
    const [reduceMotion, setReduceMotion] = useState(() => {
        const saved = localStorage.getItem('user_reduceMotion');
        return saved === 'true';
    });
    
    // Notifications state with localStorage persistence
    const [emailNotifications, setEmailNotifications] = useState(() => {
        const saved = localStorage.getItem('user_emailNotifications');
        return saved !== 'false'; // Default to true
    });

    // Persist profile changes
    useEffect(() => {
        localStorage.setItem('user_fullName', fullName);
    }, [fullName]);

    useEffect(() => {
        localStorage.setItem('user_email', email);
    }, [email]);

    useEffect(() => {
        localStorage.setItem('user_bio', bio);
    }, [bio]);

    // Persist preferences
    useEffect(() => {
        // Map display names to language codes
        const langCodeMap = { 'English': 'en', 'Arabic': 'ar', 'Hebrew': 'he', 'Urdu': 'ur', 'Persian': 'fa' };
        const langCode = langCodeMap[language] || 'en';
        setLanguage(langCode);
    }, [language]);

    useEffect(() => {
        localStorage.setItem('user_reduceMotion', reduceMotion.toString());
        // Apply reduce motion to document
        if (reduceMotion) {
            document.documentElement.style.setProperty('--animation-duration', '0s');
        } else {
            document.documentElement.style.removeProperty('--animation-duration');
        }
    }, [reduceMotion]);

    // Persist notifications
    useEffect(() => {
        localStorage.setItem('user_emailNotifications', emailNotifications.toString());
    }, [emailNotifications]);

    // Update email from auth context if available
    useEffect(() => {
        if (user?.email && !localStorage.getItem('user_email')) {
            setEmail(user.email);
        }
    }, [user]);

    const handleSignOut = async () => {
        const result = await confirm('Are you sure you want to sign out?', 'Sign Out');
        if (result) {
            try {
                await logout();
                navigate('/signin');
            } catch (error) {
                console.error('Failed to sign out:', error);
                alert('Failed to sign out. Please try again.', 'Error');
            }
        }
    };

    const handleDeleteAccount = async () => {
        const userInput = await prompt(
            'Are you absolutely sure you want to delete your account? This action is IRREVERSIBLE and will delete all your data. Type "DELETE" to confirm.',
            'Delete Account',
            'Type DELETE to confirm'
        );
        
        if (userInput === 'DELETE') {
            try {
                // Note: Direct account deletion from client requires admin API or backend endpoint
                // For now, we'll clear all local data and sign out
                // In production, you should call a backend API endpoint to handle account deletion
                
                // Clear all localStorage data
                localStorage.clear();
                
                // Sign out the user
                await logout();
                
                await alert('Your local data has been cleared. Please contact support to permanently delete your account from our servers.', 'Account Deletion');
                navigate('/signin');
            } catch (error) {
                console.error('Failed to delete account:', error);
                alert('Failed to delete account. Please contact support for assistance.', 'Error');
            }
        }
    };

    const handleChangeAvatar = () => {
        navigate('/avatar');
    };

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
                                <h3 className="text-xl font-bold text-white">{fullName || 'User'}</h3>
                                <p className="text-gray-400">Explorer & Student</p>
                                <button 
                                    onClick={handleChangeAvatar}
                                    className="mt-2 text-sm text-orange-400 hover:text-orange-300 font-medium transition-colors"
                                >
                                    Change Avatar
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-orange-200 text-xs font-bold uppercase tracking-wider">Full Name</label>
                                <input 
                                    type="text" 
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:border-orange-500 focus:outline-none transition-colors" 
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-orange-200 text-xs font-bold uppercase tracking-wider">Email Address</label>
                                <input 
                                    type="email" 
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:border-orange-500 focus:outline-none transition-colors" 
                                />
                            </div>
                            <div className="col-span-1 md:col-span-2 space-y-2">
                                <label className="text-orange-200 text-xs font-bold uppercase tracking-wider">Bio</label>
                                <textarea 
                                    rows="4" 
                                    value={bio}
                                    onChange={(e) => setBio(e.target.value)}
                                    className="w-full bg-black/60 border border-white/10 rounded-xl p-3 text-white focus:border-orange-500 focus:outline-none transition-colors resize-none"
                                />
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
                                    onChange={(e) => setLanguageState(e.target.value)}
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

                            <div className="bg-black/60 p-4 rounded-xl border border-white/10">
                                <div className="mb-3">
                                    <h3 className="text-white font-medium mb-1">User Role</h3>
                                    <p className="text-gray-400 text-sm">Switch between different role views (for testing)</p>
                                </div>
                                <select
                                    value={userRole}
                                    onChange={(e) => {
                                        const newRole = e.target.value;
                                        setUserRoleState(newRole);
                                        setUserRole(newRole);
                                        // Redirect to appropriate dashboard
                                        navigate(getDashboardPath(newRole));
                                    }}
                                    className="w-full bg-white/5 border border-white/10 text-white rounded-lg p-2 outline-none focus:border-orange-500"
                                >
                                    <option value={ROLES.STUDENT}>{getRoleDisplayName(ROLES.STUDENT)}</option>
                                    <option value={ROLES.TEACHER}>{getRoleDisplayName(ROLES.TEACHER)}</option>
                                    <option value={ROLES.PARENT}>{getRoleDisplayName(ROLES.PARENT)}</option>
                                    <option value={ROLES.ADMIN}>{getRoleDisplayName(ROLES.ADMIN)}</option>
                                </select>
                                <p className="text-xs text-gray-500 mt-2 italic">
                                    Current: {getRoleDisplayName(userRole)}
                                </p>
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
                            <button 
                                onClick={handleSignOut}
                                className="w-full flex items-center justify-between p-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded-xl transition-all group cursor-pointer"
                            >
                                <span className="text-red-400 font-medium group-hover:text-red-300">Sign Out</span>
                                <FaSignOutAlt className="text-red-400 group-hover:text-red-300" />
                            </button>
                            <button 
                                onClick={handleDeleteAccount}
                                className="w-full flex items-center justify-between p-4 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 rounded-xl transition-all group cursor-pointer"
                            >
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
        <div className="flex pt-20 sm:pt-24 min-h-screen container mx-auto px-2 sm:px-4 gap-3 sm:gap-6">
            <Sidebar />

            <main className="flex-grow flex flex-col lg:flex-row gap-4 sm:gap-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                {/* Navigation Panel */}
                <div className="w-full lg:w-64 glass-panel no-hover p-4 sm:p-6 rounded-3xl border border-white/10 h-fit">
                    <h1 className="text-xl sm:text-2xl font-bold text-white mb-6 sm:mb-8 px-2">Settings</h1>
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
                <div className="flex-grow glass-panel no-hover p-4 sm:p-6 md:p-8 rounded-3xl border border-white/10 relative overflow-hidden h-auto lg:h-[calc(100vh-140px)] overflow-y-auto custom-scrollbar">
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
