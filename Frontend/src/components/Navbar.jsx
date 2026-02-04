import React, { useEffect, useState, useRef } from 'react';
import { FaUserCircle, FaBars, FaTimes, FaGlobe, FaChevronDown } from 'react-icons/fa';
import { Link, useNavigate } from 'react-router-dom';

import logo from '../assets/logo.svg';
import { useAuth } from '../contexts/AuthContext';
import { useSidebar } from '../contexts/SidebarContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { toggleSidebar, isSidebarOpen } = useSidebar();
  const navigate = useNavigate();
  const [isLanguageOpen, setIsLanguageOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState('English');
  const languageMenuRef = useRef(null);

  useEffect(() => {
    // Initialize Google Translate if available
    const initTranslate = () => {
      if (window.google && window.google.translate && window.google.translate.TranslateElement) {
        const translateElement = document.getElementById('google_translate_element');
        if (translateElement && !translateElement.hasChildNodes()) {
          try {
            if (typeof window.googleTranslateElementInit === 'function') {
              window.googleTranslateElementInit();
            }
          } catch (error) {
            console.error('Error initializing Google Translate:', error);
          }
        }
        return true; // Successfully initialized
      }
      return false; // Not ready yet
    };

    // Load saved language preference
    const savedLang = localStorage.getItem('selected_language');
    const langNames = {
      'en': 'English',
      'hi': 'हिंदी',
      'es': 'Español',
      'fr': 'Français',
      'de': 'Deutsch',
      'it': 'Italiano',
      'pt': 'Português',
      'ru': 'Русский',
      'ja': '日本語',
      'ko': '한국어',
      'zh-CN': '中文',
      'ar': 'العربية',
      'bn': 'বাংলা',
      'gu': 'ગુજરાતી',
      'kn': 'ಕನ್ನಡ',
      'ml': 'മലയാളം',
      'mr': 'मराठी',
      'ne': 'नेपाली',
      'pa': 'ਪੰਜਾਬੀ',
      'ta': 'தமிழ்',
      'te': 'తెలుగు',
      'ur': 'اردو'
    };
    
    if (savedLang && langNames[savedLang]) {
      setCurrentLang(langNames[savedLang]);
    }

    // Wait for Google Translate to load, then initialize
    let attempts = 0;
    const maxAttempts = 50; // 5 seconds max wait
    
    const tryInit = () => {
      attempts++;
      if (initTranslate()) {
        // Successfully initialized, now set language if saved
        if (savedLang) {
          setTimeout(() => {
            const select = document.querySelector('.goog-te-combo');
            if (select && select.value !== savedLang) {
              select.value = savedLang;
              const event = new Event('change', { bubbles: true });
              select.dispatchEvent(event);
            }
          }, 300);
        }
      } else if (attempts < maxAttempts) {
        setTimeout(tryInit, 100);
      } else {
        console.warn('Google Translate failed to load after multiple attempts');
      }
    };

    // Start trying to initialize
    tryInit();
  }, []);

  useEffect(() => {
    // Close language menu when clicking outside
    const handleClickOutside = (event) => {
      if (languageMenuRef.current && !languageMenuRef.current.contains(event.target)) {
        setIsLanguageOpen(false);
      }
    };

    if (isLanguageOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isLanguageOpen]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/signin');
    } catch (error) {
      console.error('Failed to log out', error);
    }
  };

  const handleLanguageChange = (langCode) => {
    // Store selected language
    localStorage.setItem('selected_language', langCode);
    
    // Update current language state
    const langNames = {
      'en': 'English',
      'hi': 'हिंदी',
      'es': 'Español',
      'fr': 'Français',
      'de': 'Deutsch',
      'it': 'Italiano',
      'pt': 'Português',
      'ru': 'Русский',
      'ja': '日本語',
      'ko': '한국어',
      'zh-CN': '中文',
      'ar': 'العربية',
      'bn': 'বাংলা',
      'gu': 'ગુજરાતી',
      'kn': 'ಕನ್ನಡ',
      'ml': 'മലയാളം',
      'mr': 'मराठी',
      'ne': 'नेपाली',
      'pa': 'ਪੰਜਾਬੀ',
      'ta': 'தமிழ்',
      'te': 'తెలుగు',
      'ur': 'اردو'
    };
    setCurrentLang(langNames[langCode] || 'English');
    setIsLanguageOpen(false);
    
    // Function to trigger Google Translate using multiple methods
    const triggerTranslation = () => {
      // Method 1: Try to find and use the select element directly
      const selectors = [
        '.goog-te-combo',
        'select.goog-te-combo',
        '#\\:0\\.targetLanguage',
        'select[id*="targetLanguage"]',
        'select[class*="goog-te"]'
      ];
      
      for (const selector of selectors) {
        try {
          const select = document.querySelector(selector);
          if (select && select.tagName === 'SELECT') {
            // Set the value
            if (select.value !== langCode) {
              select.value = langCode;
            }
            
            // Create and dispatch change event
            const changeEvent = new Event('change', { bubbles: true, cancelable: true });
            select.dispatchEvent(changeEvent);
            
            // Also try input event
            const inputEvent = new Event('input', { bubbles: true, cancelable: true });
            select.dispatchEvent(inputEvent);
            
            // Try onchange if it exists
            if (typeof select.onchange === 'function') {
              try {
                select.onchange(changeEvent);
              } catch (e) {
                // Ignore errors
              }
            }
            
            return true;
          }
        } catch (e) {
          // Continue to next selector
        }
      }
      
      // Method 2: Try to access Google Translate iframe
      try {
        const iframes = document.querySelectorAll('iframe');
        for (const iframe of iframes) {
          try {
            if (iframe.src && iframe.src.includes('translate.google.com')) {
              const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
              if (iframeDoc) {
                const iframeSelect = iframeDoc.querySelector('select');
                if (iframeSelect) {
                  iframeSelect.value = langCode;
                  const changeEvent = new Event('change', { bubbles: true });
                  iframeSelect.dispatchEvent(changeEvent);
                  return true;
                }
              }
            }
          } catch (e) {
            // Cross-origin restrictions, continue
          }
        }
      } catch (e) {
        // Ignore iframe access errors
      }
      
      // Method 3: Use cookie-based approach (Google Translate uses cookies)
      // Get current domain for cookie
      const domain = window.location.hostname;
      const cookiePath = '/';
      
      if (langCode === 'en') {
        // Remove translation cookie to show English
        document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${cookiePath};`;
        document.cookie = `googtrans=/en/en; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=${cookiePath};`;
      } else {
        // Set translation cookie - don't set domain to avoid cookie rejection
        const expireDate = new Date();
        expireDate.setFullYear(expireDate.getFullYear() + 1);
        document.cookie = `googtrans=/en/${langCode}; expires=${expireDate.toUTCString()}; path=${cookiePath}; SameSite=Lax`;
      }
      
      // Method 4: Reload page with translation cookie (last resort)
      if (langCode !== 'en') {
        window.location.reload();
        return true;
      }
      
      return false;
    };
    
    // Try to trigger translation immediately
    if (!triggerTranslation()) {
      // If not found, wait and retry
      let attempts = 0;
      const maxAttempts = 15;
      
      const retry = () => {
        attempts++;
        if (triggerTranslation()) {
          return; // Success
        }
        if (attempts < maxAttempts) {
          setTimeout(retry, 200);
        } else {
          // Final fallback: reload page with cookie
          if (langCode !== 'en') {
            const expireDate = new Date();
            expireDate.setFullYear(expireDate.getFullYear() + 1);
            document.cookie = `googtrans=/en/${langCode}; expires=${expireDate.toUTCString()}; path=/;`;
            window.location.reload();
          }
        }
      };
      
      setTimeout(retry, 300);
    }
  };

  const getCurrentLanguage = () => {
    const langNames = {
      'en': 'English',
      'hi': 'हिंदी',
      'es': 'Español',
      'fr': 'Français',
      'de': 'Deutsch',
      'it': 'Italiano',
      'pt': 'Português',
      'ru': 'Русский',
      'ja': '日本語',
      'ko': '한국어',
      'zh-CN': '中文',
      'ar': 'العربية',
      'bn': 'বাংলা',
      'gu': 'ગુજરાતી',
      'kn': 'ಕನ್ನಡ',
      'ml': 'മലയാളം',
      'mr': 'मराठी',
      'ne': 'नेपाली',
      'pa': 'ਪੰਜਾਬੀ',
      'ta': 'தமிழ்',
      'te': 'తెలుగు',
      'ur': 'اردو'
    };

    // Try to get from Google Translate select
    if (window.google && window.google.translate) {
      const select = document.querySelector('.goog-te-combo');
      if (select && select.value) {
        return langNames[select.value] || 'English';
      }
    }

    // Fallback to saved preference
    const savedLang = localStorage.getItem('selected_language');
    if (savedLang && langNames[savedLang]) {
      return langNames[savedLang];
    }

    return currentLang;
  };

  const languages = [
    { code: 'en', name: 'English', native: 'English' },
    { code: 'hi', name: 'Hindi', native: 'हिंदी' },
    { code: 'es', name: 'Spanish', native: 'Español' },
    { code: 'fr', name: 'French', native: 'Français' },
    { code: 'de', name: 'German', native: 'Deutsch' },
    { code: 'it', name: 'Italian', native: 'Italiano' },
    { code: 'pt', name: 'Portuguese', native: 'Português' },
    { code: 'ru', name: 'Russian', native: 'Русский' },
    { code: 'ja', name: 'Japanese', native: '日本語' },
    { code: 'ko', name: 'Korean', native: '한국어' },
    { code: 'zh-CN', name: 'Chinese', native: '中文' },
    { code: 'ar', name: 'Arabic', native: 'العربية' },
    { code: 'bn', name: 'Bengali', native: 'বাংলা' },
    { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
    { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
    { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
    { code: 'mr', name: 'Marathi', native: 'मराठी' },
    { code: 'ne', name: 'Nepali', native: 'नेपाली' },
    { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
    { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
    { code: 'te', name: 'Telugu', native: 'తెలుగు' },
    { code: 'ur', name: 'Urdu', native: 'اردو' }
  ];

  return (
    <nav className="absolute top-0 left-0 w-full z-50 py-3 sm:py-6 transition-all duration-300">
      <div className="container mx-auto px-3 sm:px-6">
        <div className="glass-panel px-4 sm:px-8 py-3 sm:py-4 rounded-full flex items-center justify-between bg-black/60 backdrop-blur-xl border-white/5">

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

            <Link to="/" className="flex items-center gap-2 sm:gap-3 cursor-pointer group">
              <img src={logo} alt="Gurukul Logo" className="h-6 w-6 sm:h-8 sm:w-8 object-contain" />
              <span className="text-lg sm:text-2xl font-bold font-heading tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400 group-hover:to-white transition-all">
                Gurukul
              </span>
            </Link>
          </div>

          {/* Links & Actions */}
          <div className="flex items-center gap-2 sm:gap-4 lg:gap-8">
            {/* Language Selector */}
            <div className="relative" ref={languageMenuRef}>
              <button
                onClick={() => setIsLanguageOpen(!isLanguageOpen)}
                className="flex items-center gap-2 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full bg-black/40 hover:bg-black/60 text-gray-300 hover:text-white transition-all border border-white/5 text-xs sm:text-sm"
                title="Change Language"
              >
                <FaGlobe className="text-sm sm:text-base" />
                <span className="hidden sm:inline">{currentLang}</span>
                <FaChevronDown className={`text-[10px] transition-transform ${isLanguageOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Language Dropdown */}
              {isLanguageOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 sm:w-56 bg-[#0a0c08] border border-white/5 rounded-xl shadow-2xl overflow-hidden z-50 max-h-[400px] overflow-y-auto custom-scrollbar">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => handleLanguageChange(lang.code)}
                      className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:bg-black/40 hover:text-orange-400 transition-colors flex items-center justify-between border-b border-white/5 last:border-b-0"
                    >
                      <div className="flex flex-col">
                        <span className="font-medium">{lang.native}</span>
                        <span className="text-xs text-gray-500">{lang.name}</span>
                      </div>
                      {currentLang === lang.native && (
                        <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                      )}
                    </button>
                  ))}
                </div>
              )}

              {/* Hidden Google Translate Element */}
              <div id="google_translate_element" className="hidden"></div>
            </div>

            {/* Sign In Section */}
            <div className="hidden lg:flex items-center">
              {user ? (
                <div className="flex items-center gap-2 sm:gap-4">
                  <div className="text-xs sm:text-sm text-gray-300 flex items-center gap-1 sm:gap-2">
                    <FaUserCircle className="text-base sm:text-lg" />
                    <span className="hidden xl:inline">{user.email?.split('@')[0] || user.full_name || 'User'}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="text-xs font-bold px-3 sm:px-4 py-1.5 sm:py-2 rounded-full bg-red-500/10 hover:bg-red-500/20 text-red-500 transition-all border border-red-500/20"
                  >
                    Log Out
                  </button>
                </div>
              ) : (
                <Link to="/signin" className="text-xs font-bold px-4 sm:px-6 py-1.5 sm:py-2 rounded-full bg-black/60 hover:bg-black/80 text-white transition-all border border-white/5 shadow-lg">
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
