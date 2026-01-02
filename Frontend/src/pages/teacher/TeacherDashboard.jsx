import React from 'react';
import Sidebar from '../../components/Sidebar';
import { FaUsers, FaBookOpen, FaClipboardCheck, FaChartBar, FaUserGraduate } from 'react-icons/fa';

const TeacherDashboard = () => {
    // Mock data - would come from backend
    const stats = {
        totalStudents: 45,
        activeClasses: 3,
        assignmentsPending: 12,
        averageScore: 78
    };

    const recentActivity = [
        { student: 'Arjun', action: 'Completed quiz', subject: 'Mathematics', time: '2 hours ago' },
        { student: 'Priya', action: 'Submitted assignment', subject: 'Physics', time: '5 hours ago' },
        { student: 'Rohan', action: 'Started new topic', subject: 'Chemistry', time: '1 day ago' }
    ];

    const StatCard = ({ icon: Icon, title, value, subtitle, color }) => (
        <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/10 relative overflow-hidden">
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
                    <h2 className="text-2xl sm:text-3xl font-bold font-heading text-white">Teacher Dashboard</h2>
                    <p className="text-gray-200 text-xs sm:text-sm font-medium">
                        Manage your classes and track student progress
                    </p>
                </div>

                {/* Statistics */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <StatCard
                        icon={FaUserGraduate}
                        title="Total Students"
                        value={stats.totalStudents}
                        subtitle="Across all classes"
                        color="bg-blue-500/20"
                    />
                    <StatCard
                        icon={FaBookOpen}
                        title="Active Classes"
                        value={stats.activeClasses}
                        subtitle="Currently teaching"
                        color="bg-green-500/20"
                    />
                    <StatCard
                        icon={FaClipboardCheck}
                        title="Pending Reviews"
                        value={stats.assignmentsPending}
                        subtitle="Needs attention"
                        color="bg-orange-500/20"
                    />
                    <StatCard
                        icon={FaChartBar}
                        title="Average Score"
                        value={`${stats.averageScore}%`}
                        subtitle="Class performance"
                        color="bg-purple-500/20"
                    />
                </div>

                {/* Recent Activity */}
                <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/10 mb-6">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <FaUsers className="text-orange-400" />
                        Recent Student Activity
                    </h3>
                    <div className="space-y-3">
                        {recentActivity.map((activity, idx) => (
                            <div key={idx} className="p-3 bg-white/5 rounded-lg border border-white/5">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <span className="text-white font-medium">{activity.student}</span>
                                        <span className="text-gray-400 text-sm ml-2">{activity.action}</span>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xs text-gray-400">{activity.subject}</div>
                                        <div className="text-xs text-gray-500">{activity.time}</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/10">
                        <h3 className="text-lg font-semibold text-white mb-4">Class Management</h3>
                        <div className="space-y-2">
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                View All Students
                            </button>
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Create Assignment
                            </button>
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Grade Submissions
                            </button>
                        </div>
                    </div>

                    <div className="glass-panel p-4 sm:p-6 rounded-2xl border border-white/10">
                        <h3 className="text-lg font-semibold text-white mb-4">Progress Tracking</h3>
                        <div className="space-y-2">
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Student Reports
                            </button>
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Class Analytics
                            </button>
                            <button className="w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-sm text-gray-300">
                                Performance Insights
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default TeacherDashboard;

