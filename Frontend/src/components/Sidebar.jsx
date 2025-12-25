import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    FaThLarge,
    FaBookOpen,
    FaFileAlt,
    FaComments,
    FaClipboardList,
    FaVideo,
    FaRobot,
    FaUserAstronaut,
    FaCog
} from 'react-icons/fa';

const menuItems = [
    { icon: FaThLarge, label: "Dashboard", path: "/dashboard" },
    { icon: FaBookOpen, label: "Subjects", path: "/subjects" },
    { icon: FaFileAlt, label: "Summarizer", path: "/summarizer" },
    { icon: FaComments, label: "Chatbot", path: "/chatbot" },
    { icon: FaClipboardList, label: "Test", path: "/test" },
    { icon: FaVideo, label: "Lectures", path: "/lectures" },
    { icon: FaRobot, label: "Agent Simulator", path: "/agent-simulator" },
    { icon: FaUserAstronaut, label: "Avatar", path: "/avatar" },
];

const Sidebar = () => {
    return (
        <aside className="w-64 flex flex-col gap-2 h-[calc(100vh-100px)] sticky top-24 ml-4">
            <div className="glass-panel p-3 flex-grow flex flex-col justify-between border border-white/10 shadow-xl rounded-2xl overflow-hidden">

                {/* Main Menu */}
                <div className="flex flex-col gap-2">
                    {menuItems.map((item, index) => (
                        <NavLink
                            key={index}
                            to={item.path}
                            className={({ isActive }) => `
                flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 group
                ${isActive
                                    ? 'bg-gradient-to-r from-orange-600 to-amber-600 text-white shadow-lg border border-white/20 transform scale-105'
                                    : 'bg-white/5 text-gray-300 hover:text-white hover:pl-6 border border-transparent'}
              `}
                        >
                            <item.icon className="text-lg opacity-80 group-hover:opacity-100" />
                            <span className="text-sm font-medium tracking-wide">{item.label}</span>
                        </NavLink>
                    ))}
                </div>

                {/* Settings at Bottom */}
                <div className="pt-3 border-t border-white/10 mt-2">
                    <NavLink
                        to="/settings"
                        className={({ isActive }) => `
              flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 group
              ${isActive
                                ? 'bg-gradient-to-r from-gray-700 to-gray-600 text-white shadow-lg border border-white/20'
                                : 'bg-white/5 text-gray-300 hover:text-white border border-transparent'}
            `}
                    >
                        <FaCog className="text-lg opacity-80 group-hover:opacity-100" />
                        <span className="text-sm font-medium tracking-wide">Settings</span>
                    </NavLink>
                </div>

            </div>
        </aside>
    );
};

export default Sidebar;
