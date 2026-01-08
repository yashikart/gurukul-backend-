// Automatically detect if running on localhost
const isLocalhost = typeof window !== 'undefined' && 
    (window.location.hostname === 'localhost' || 
     window.location.hostname === '127.0.0.1' ||
     window.location.hostname === '');

// In development mode (Vite), always use localhost (override env variable)
// Otherwise, use environment variable if set, or detect based on hostname
const API_BASE_URL = (import.meta.env.DEV || isLocalhost) 
    ? 'http://localhost:3000' 
    : (import.meta.env.VITE_API_URL || 'https://gurukul-backend-kap2.onrender.com');

// Debug log in development
if (import.meta.env.DEV) {
    console.log('API Config:', {
        VITE_API_URL: import.meta.env.VITE_API_URL,
        isDev: import.meta.env.DEV,
        hostname: typeof window !== 'undefined' ? window.location.hostname : 'N/A',
        isLocalhost,
        API_BASE_URL
    });
}

// Build version for cache busting
export const BUILD_VERSION = '2026-01-06-v2';

// Updated: 2026-01-06 - Auto-detects localhost vs production
export default API_BASE_URL;
