import { createContext, useContext, useEffect, useState } from 'react';
import API_BASE_URL from '../config';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [token, setToken] = useState(() => {
        // Get token from localStorage
        return localStorage.getItem('auth_token') || null;
    });

    // Log runtime API configuration to help debug connectivity issues in production
    if (typeof window !== 'undefined') {
        // This will run on initial render in the browser only
        // eslint-disable-next-line no-console
        console.log('[Auth] Runtime API_BASE_URL:', API_BASE_URL, 'hostname:', window.location.hostname);
    }

    // Check if user is authenticated on mount
    useEffect(() => {
        const checkAuth = async () => {
            const storedToken = localStorage.getItem('auth_token');
            if (storedToken) {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
                        headers: {
                            'Authorization': `Bearer ${storedToken}`
                        },
                        // Add timeout to prevent hanging
                        signal: AbortSignal.timeout(10000) // 10 second timeout
                    });
                    
                    if (response.ok) {
                        const userData = await response.json();
                        setUser({
                            id: userData.id,
                            email: userData.email,
                            full_name: userData.full_name,
                            role: userData.role
                        });
                    } else if (response.status === 401) {
                        // Only logout on actual 401 Unauthorized (token is invalid/expired)
                        console.warn('[Auth] Token invalid (401), logging out');
                        localStorage.removeItem('auth_token');
                        localStorage.removeItem('ems_token');
                        setToken(null);
                        setUser(null);
                    } else {
                        // For other errors (500, 503, network issues, etc.), keep user logged in
                        // They might have a valid token but server is temporarily unavailable
                        console.warn('[Auth] Auth check failed with status:', response.status, '- keeping session active');
                        // Don't clear token or logout - just don't set user state
                        // User can still use the app, and we'll retry on next page load
                    }
                } catch (error) {
                    // Network errors, timeouts, CORS issues - don't logout
                    // User might have valid token but connection is temporarily unavailable
                    if (error.name === 'AbortError' || error.message.includes('timeout')) {
                        console.warn('[Auth] Auth check timed out - keeping session active');
                    } else if (error instanceof TypeError && error.message.includes('fetch')) {
                        console.warn('[Auth] Network error during auth check - keeping session active');
                    } else {
                        console.warn('[Auth] Auth check error:', error.message, '- keeping session active');
                    }
                    // Don't clear token or logout on network errors
                    // User stays logged in and can continue using the app
                }
            }
            setLoading(false);
        };
        
        checkAuth();
    }, []);

    const login = async (email, password) => {
        try {
            console.log('[Auth] Attempting login to:', `${API_BASE_URL}/api/v1/auth/login`);
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });
            
            console.log('[Auth] Login response status:', response.status);

            if (!response.ok) {
                let errorMessage = 'Login failed';
                try {
                    const error = await response.json();
                    errorMessage = error.detail || error.message || 'Login failed';
                } catch (e) {
                    // If response is not JSON, use status text
                    errorMessage = response.statusText || 'Login failed';
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            
            // Store token
            localStorage.setItem('auth_token', data.access_token);
            setToken(data.access_token);
            
            // Extract session_id from token (backend includes it in JWT payload)
            const contextManager = (await import('../utils/contextManager')).default;
            const sessionId = contextManager.extractSessionIdFromToken(data.access_token);
            if (sessionId) {
              localStorage.setItem('session_id', sessionId);
              console.log('[Auth] Session ID extracted from token:', sessionId);
            } else {
              console.warn('[Auth] No session_id found in token');
            }
            
            // Set user
            setUser(data.user);
            
            return { session: { access_token: data.access_token }, user: data.user };
        } catch (error) {
            // Handle network errors
            if (error instanceof TypeError && error.message.includes('fetch')) {
                throw new Error('Unable to connect to server. Please check your internet connection.');
            }
            throw error;
        }
    };

    const signup = async (email, password, role, full_name) => {
        try {
            console.log('[Auth] Attempting registration to:', `${API_BASE_URL}/api/v1/auth/register`);
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email, 
                    password, 
                    role: role || 'STUDENT',
                    full_name: full_name || null
                }),
            });
            
            console.log('[Auth] Registration response status:', response.status);

            if (!response.ok) {
                let errorMessage = 'Registration failed';
                try {
                    const error = await response.json();
                    errorMessage = error.detail || error.message || 'Registration failed';
                } catch (e) {
                    // If response is not JSON, use status text
                    errorMessage = response.statusText || 'Registration failed';
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            
            // Store token
            localStorage.setItem('auth_token', data.access_token);
            setToken(data.access_token);
            
            // Set user
            setUser(data.user);
            
            return { user: data.user, session: { access_token: data.access_token } };
        } catch (error) {
            // Handle network errors
            if (error instanceof TypeError && error.message.includes('fetch')) {
                throw new Error('Unable to connect to server. Please check your internet connection.');
            }
            throw error;
        }
    };

    const logout = async () => {
        // Clear token and user
        localStorage.removeItem('auth_token');
        // Clear EMS authentication to prevent cross-account contamination
        localStorage.removeItem('ems_token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, signup, logout, loading, token }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};
