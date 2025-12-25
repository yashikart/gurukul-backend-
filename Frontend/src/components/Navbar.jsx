import React, { useState, useEffect, useRef } from 'react';
import { FaGlobe, FaChevronDown } from 'react-icons/fa';
import { Link } from 'react-router-dom';

import logo from '../assets/logo.svg';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [language, setLanguage] = useState('English');
  const dropdownRef = useRef(null);

  // Initialize language based on cookie
  useEffect(() => {
    // Check for googtrans cookie
    const getCookie = (name) => {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    };

    const googtrans = getCookie('googtrans');
    if (googtrans === '/en/ar') {
      setLanguage('Arabic');
    } else {
      setLanguage('English');
    }

    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLanguageSelect = (lang) => {
    setLanguage(lang);
    setIsOpen(false);

    // Programmatically find the hidden Google Translate dropdown and select the language
    const changeLanguage = () => {
      const combo = document.querySelector('.goog-te-combo');
      if (combo) {
        combo.value = lang === 'Arabic' ? 'ar' : 'en';
        combo.dispatchEvent(new Event('change', { bubbles: true }));
        combo.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        // Retry once if not found immediately (sometimes script lazy loads)
        setTimeout(() => {
          const retryCombo = document.querySelector('.goog-te-combo');
          if (retryCombo) {
            retryCombo.value = lang === 'Arabic' ? 'ar' : 'en';
            retryCombo.dispatchEvent(new Event('change', { bubbles: true }));
            retryCombo.dispatchEvent(new Event('input', { bubbles: true }));
          }
        }, 500);
      }
    };

    changeLanguage();
  };

  return (
    <nav className="absolute top-0 left-0 w-full z-50 py-6 transition-all duration-300">
      <div className="container mx-auto px-6">
        <div className="glass-panel px-8 py-4 rounded-full flex items-center justify-between bg-black/60 backdrop-blur-xl border-white/5">

          {/* Brand */}
          <Link to="/" className="flex items-center gap-3 cursor-pointer group">
            <img src={logo} alt="Gurukul Logo" className="h-8 w-8 object-contain" />
            <span className="text-2xl font-bold font-heading tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 group-hover:to-white transition-all">
              Gurukul
            </span>
          </Link>

          {/* Links & Actions */}
          <div className="flex items-center gap-8">
            <a href="#about" className="text-sm font-medium text-gray-300 hover:text-white transition-colors tracking-wide">
              About
            </a>

            <div className="h-4 w-px bg-white/10"></div>

            {/* Google Translate Widget (Hidden) */}
            <div id="google_translate_element" style={{ display: 'none' }}></div>

            {/* Custom Language Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 text-sm text-gray-300 hover:text-white transition-colors group px-2 py-1 rounded-lg hover:bg-white/5"
              >
                <FaGlobe className="group-hover:text-accent transition-colors" />
                <span>{language}</span>
                <FaChevronDown className={`text-xs transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Dropdown Menu */}
              {isOpen && (
                <div className="absolute top-full right-0 mt-2 w-32 bg-black/95 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden shadow-xl animate-in fade-in zoom-in-95 duration-200">
                  <div className="py-1">
                    {['English', 'Arabic'].map((lang) => (
                      <button
                        key={lang}
                        onClick={() => handleLanguageSelect(lang)}
                        className={`w-full text-left px-4 py-2 text-sm transition-colors hover:bg-white/10 ${language === lang ? 'text-white bg-white/5 font-medium' : 'text-gray-400'
                          }`}
                      >
                        {lang}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Sign In Section */}
            <div className="flex items-center pl-4 border-l border-white/10">
              <Link to="/signin" className="text-xs font-bold px-6 py-2 rounded-full bg-white/10 hover:bg-white/20 text-white transition-all border border-white/10 shadow-lg">
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
