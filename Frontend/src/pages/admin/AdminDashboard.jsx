import React from 'react';
import Sidebar from '../../components/Sidebar';
import { FaUsers, FaChartLine, FaCog, FaShieldAlt, FaServer, FaExclamationTriangle } from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';
import UserManagement from './UserManagement';

const AdminDashboard = () => {
    const { user } = useAuth();

    // Mock data - would come from backend in production
    const stats = {
        totalUsers: 1250,
        activeUsers: 890,
        totalTeachers: 45,
        totalStudents: 1150,
        totalParents: 55,
        systemHealth: 'healthy',
        apiStatus: 'operational'
    };

    const StatCard = ({ icon: Icon, title, value, subtitle, color }) => (
        <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/10 relative overflow-hidden group">
            <div className="flex items-center justify-between mb-4">
                <div className={`p-2 rounded-lg ${color} opacity-20`}>
                    <Icon className={`text-lg ${color.replace('bg-', 'text-')}`} />
                </div>
                <span className="text-xs text-gray-400">{title}</span>
            </div>
            <div className="text-2xl sm:text-3xl font-bold text-white mb-1 tabular-nums">{value}</div>
            {subtitle && <div className="text-xs text-gray-400">{subtitle}</div>}
        </div>
    );

    return (
        <div className="flex pt-20 sm:pt-24 min-h-screen container mx-auto px-2 sm:px-4 gap-3 sm:gap-6">
            <Sidebar />
            <main className="flex-grow animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <div className="mb-6 sm:mb-8">
                    <h2 className="text-2xl sm:text-3xl font-bold font-heading text-white">Administrator Dashboard</h2>
                    <p className="text-gray-200 text-xs sm:text-sm font-medium">
                        Platform oversight and management
                    </p>
                </div>

                {/* System Status */}
                <div className="mb-6 glass-panel p-4 sm:p-6 rounded-2xl border border-white/10">
                    <div className="flex items-center gap-3 mb-4">
                        <FaServer className="text-green-400 text-xl" />
                        <h3 className="text-lg font-semibold text-white">System Status</h3>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                            <span className="text-sm text-gray-300">Backend API</span>
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold">
                                {stats.apiStatus}
                            </span>
                        </div>
                        <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                            <span className="text-sm text-gray-300">System Health</span>
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold">
                                {stats.systemHealth}
                            </span>
                        </div>
                    </div>
                </div>

                {/* User Statistics */}
                <div className="mb-6">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <FaUsers className="text-orange-400" />
                        User Statistics
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <StatCard
                            icon={FaUsers}
                            title="Total Users"
                            value={stats.totalUsers}
                            subtitle={`${stats.activeUsers} active`}
                            color="bg-blue-500/20"
                        />
                        <StatCard
                            icon={FaUsers}
                            title="Students"
                            value={stats.totalStudents}
                            subtitle="Active learners"
                            color="bg-green-500/20"
                        />
                        <StatCard
                            icon={FaUsers}
                            title="Teachers"
                            value={stats.totalTeachers}
                            subtitle="Educators"
                            color="bg-purple-500/20"
                        />
                        <StatCard
                            icon={FaUsers}
                            title="Parents"
                            value={stats.totalParents}
                            subtitle="Guardians"
                            color="bg-orange-500/20"
                        />
                    </div>
                </div>

                {/* User Management Section */}
                <div className="mb-6">
                    <UserManagement />
                </div>

                {/* Quick Actions (Remaining) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/10">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <FaCog className="text-orange-400" />
                            Platform Management
                        </h3>
                        <div className="space-y-2">
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Content Moderation
                            </button>
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                System Settings
                            </button>
                        </div>
                    </div>

                    <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/10">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <FaChartLine className="text-orange-400" />
                            Analytics & Reports
                        </h3>
                        <div className="space-y-2">
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Platform Analytics
                            </button>
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Usage Reports
                            </button>
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Performance Metrics
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default AdminDashboard;

