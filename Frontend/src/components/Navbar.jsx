import React from 'react';
import { FaUserCircle, FaBars, FaTimes } from 'react-icons/fa';
import { Link, useNavigate } from 'react-router-dom';

import logo from '../assets/logo.svg';
import { useAuth } from '../contexts/AuthContext';
import { useSidebar } from '../contexts/SidebarContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { toggleSidebar, isSidebarOpen } = useSidebar();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/signin');
    } catch (error) {
      console.error('Failed to log out', error);
    }
  };

  return (
    <nav className="absolute top-0 left-0 w-full z-50 py-6 transition-all duration-300">
      <div className="container mx-auto px-6">
        <div className="glass-panel px-8 py-4 rounded-full flex items-center justify-between bg-black/60 backdrop-blur-xl border-white/5">

          {/* Brand & Toggle */}
          <div className="flex items-center gap-4">
            {/* Mobile Sidebar Toggle - Visible only when user is logged in (sidebar exists) */}
            {user && (
              <button
                onClick={toggleSidebar}
                className="lg:hidden text-gray-300 hover:text-white transition-colors"
              >
                {isSidebarOpen ? <FaTimes size={20} /> : <FaBars size={20} />}
              </button>
            )}

            <Link to="/" className="flex items-center gap-3 cursor-pointer group">
              <img src={logo} alt="Gurukul Logo" className="h-8 w-8 object-contain" />
              <span className="text-2xl font-bold font-heading tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 group-hover:to-white transition-all">
                Gurukul
              </span>
            </Link>
          </div>

          {/* Links & Actions */}
          <div className="flex items-center gap-8">
            {/* Sign In Section */}
            <div className="flex items-center">
              {user ? (
                <div className="flex items-center gap-4">
                  <div className="text-sm text-gray-300 flex items-center gap-2">
                    <FaUserCircle className="text-lg" />
                    <span className="hidden md:block">{user.email.split('@')[0]}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="text-xs font-bold px-4 py-2 rounded-full bg-red-500/10 hover:bg-red-500/20 text-red-500 transition-all border border-red-500/20"
                  >
                    Log Out
                  </button>
                </div>
              ) : (
                <Link to="/signin" className="text-xs font-bold px-6 py-2 rounded-full bg-white/10 hover:bg-white/20 text-white transition-all border border-white/10 shadow-lg">
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
