import React, { useState } from 'react';
import AdminSidebar from '../../components/AdminSidebar';
import { FaUsers, FaChartLine, FaCog, FaServer } from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';
import UserManagement from './UserManagement';
import SystemOverview from './SystemOverview';

const AdminDashboard = () => {
    const { user } = useAuth();
    const [activeSection, setActiveSection] = useState('overview'); // overview, users, reports, settings

    // Determine active section from hash or default
    React.useEffect(() => {
        const hash = window.location.hash.replace('#', '');
        if (hash && ['overview', 'users', 'reports', 'settings'].includes(hash)) {
            setActiveSection(hash);
        }
        
        // Listen for hash changes
        const handleHashChange = () => {
            const newHash = window.location.hash.replace('#', '');
            if (newHash && ['overview', 'users', 'reports', 'settings'].includes(newHash)) {
                setActiveSection(newHash);
            }
        };
        
        window.addEventListener('hashchange', handleHashChange);
        return () => window.removeEventListener('hashchange', handleHashChange);
    }, []);

    const renderContent = () => {
        switch (activeSection) {
            case 'users':
                return <UserManagement />;
            case 'overview':
            default:
                return <SystemOverview />;
            case 'reports':
                return (
                    <div className="glass-panel p-6 rounded-2xl border border-white/10">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <FaChartLine className="text-orange-500" />
                            Reports & Analytics
                        </h3>
                        <p className="text-gray-400">Reports and analytics coming soon...</p>
                    </div>
                );
            case 'settings':
                return (
                    <div className="glass-panel p-6 rounded-2xl border border-white/10">
                        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <FaCog className="text-orange-500" />
                            Platform Settings
                        </h3>
                        <p className="text-gray-400">Platform settings coming soon...</p>
                    </div>
                );
        }
    };

    return (
        <div className="flex pt-20 sm:pt-24 min-h-screen container mx-auto px-2 sm:px-4 gap-3 sm:gap-6">
            <AdminSidebar />
            <main className="flex-grow animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <div className="mb-6 sm:mb-8">
                    <h2 className="text-2xl sm:text-3xl font-bold font-heading text-white">Administrator Dashboard</h2>
                    <p className="text-gray-200 text-xs sm:text-sm font-medium">
                        Platform oversight and management
                    </p>
                </div>

                {/* Content Section */}
                <div className="mb-6">
                    {renderContent()}
                </div>
            </main>
        </div>
    );
};

export default AdminDashboard;

