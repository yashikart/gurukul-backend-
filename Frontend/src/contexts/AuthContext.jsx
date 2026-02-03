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
        
        // Test backend connectivity on page load
        // Use longer timeout for Render cold starts (free tier services can take 30+ seconds to wake up)
        (async () => {
            try {
                console.log('[Auth] Testing backend connectivity to:', `${API_BASE_URL}/health`);
                const healthResponse = await fetch(`${API_BASE_URL}/health`, {
                    method: 'GET',
                    signal: AbortSignal.timeout(30000) // 30 second timeout for Render cold starts
                });
                console.log('[Auth] Backend health check status:', healthResponse.status);
                if (healthResponse.ok) {
                    const healthData = await healthResponse.json();
                    console.log('[Auth] Backend is reachable! Health data:', healthData);
                } else {
                    console.warn('[Auth] Backend health check returned non-OK status:', healthResponse.status);
                }
            } catch (error) {
                console.error('[Auth] Backend connectivity test FAILED:', error);
                console.error('[Auth] Error type:', error.constructor.name);
                console.error('[Auth] Error message:', error.message);
                if (error.name === 'TimeoutError' || error.message.includes('timeout')) {
                    console.warn('[Auth] Backend may be waking up from sleep (Render free tier). This is normal and requests will work once it\'s ready.');
                } else {
                    console.error('[Auth] This suggests the backend URL may be wrong or CORS is blocking requests');
                }
            }
        })();
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
                        // Add timeout to prevent hanging - longer for Render cold starts
                        signal: AbortSignal.timeout(30000) // 30 second timeout for Render cold starts
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
        const loginUrl = `${API_BASE_URL}/api/v1/auth/login`;
        console.log('[Auth] ===== LOGIN DEBUG =====');
        console.log('[Auth] Runtime API_BASE_URL:', API_BASE_URL);
        console.log('[Auth] Full login URL:', loginUrl);
        console.log('[Auth] Hostname:', typeof window !== 'undefined' ? window.location.hostname : 'N/A');
        console.log('[Auth] Attempting login...');
        
        try {
            const response = await fetch(loginUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
                signal: AbortSignal.timeout(30000) // 30 second timeout for Render cold starts
            });
            
            console.log('[Auth] Login response status:', response.status);
            console.log('[Auth] Response OK:', response.ok);

            if (!response.ok) {
                let errorMessage = 'Login failed';
                try {
                    const error = await response.json();
                    errorMessage = error.detail || error.message || 'Login failed';
                    console.error('[Auth] Login error response:', error);
                } catch (e) {
                    // If response is not JSON, use status text
                    errorMessage = response.statusText || 'Login failed';
                    console.error('[Auth] Failed to parse error response:', e);
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log('[Auth] Login successful!');
            
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
            console.error('[Auth] ===== LOGIN ERROR DETAILS =====');
            console.error('[Auth] Error type:', error.constructor.name);
            console.error('[Auth] Error message:', error.message);
            console.error('[Auth] Error stack:', error.stack);
            console.error('[Auth] Full error object:', error);
            
            // Handle network errors with more detail
            if (error.name === 'TimeoutError' || error.message.includes('timeout')) {
                console.error('[Auth] Request timed out - backend may be waking up from sleep');
                throw new Error('Server is taking longer than expected to respond. This may happen if the server is waking up. Please try again in a few seconds.');
            } else if (error instanceof TypeError) {
                console.error('[Auth] TypeError detected - likely network/CORS issue');
                console.error('[Auth] Error message contains "fetch":', error.message.includes('fetch'));
                console.error('[Auth] Error message contains "Failed":', error.message.includes('Failed'));
                // Still throw the generic message for user, but log everything
                throw new Error('Unable to connect to server. The server may be starting up. Please try again in a few moments.');
            }
            throw error;
        }
    };

    const signup = async (email, password, role, full_name) => {
        const signupUrl = `${API_BASE_URL}/api/v1/auth/register`;
        console.log('[Auth] ===== SIGNUP DEBUG =====');
        console.log('[Auth] Runtime API_BASE_URL:', API_BASE_URL);
        console.log('[Auth] Full signup URL:', signupUrl);
        console.log('[Auth] Hostname:', typeof window !== 'undefined' ? window.location.hostname : 'N/A');
        console.log('[Auth] Attempting registration...');
        
        try {
            const response = await fetch(signupUrl, {
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
                signal: AbortSignal.timeout(30000) // 30 second timeout for Render cold starts
            });
            
            console.log('[Auth] Registration response status:', response.status);
            console.log('[Auth] Response OK:', response.ok);
            console.log('[Auth] Response headers:', Object.fromEntries(response.headers.entries()));

            if (!response.ok) {
                let errorMessage = 'Registration failed';
                try {
                    const error = await response.json();
                    errorMessage = error.detail || error.message || 'Registration failed';
                    console.error('[Auth] Registration error response:', error);
                } catch (e) {
                    // If response is not JSON, use status text
                    errorMessage = response.statusText || 'Registration failed';
                    console.error('[Auth] Failed to parse error response:', e);
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log('[Auth] Registration successful!');
            
            // Store token
            localStorage.setItem('auth_token', data.access_token);
            setToken(data.access_token);
            
            // Set user
            setUser(data.user);
            
            return { user: data.user, session: { access_token: data.access_token } };
        } catch (error) {
            console.error('[Auth] ===== SIGNUP ERROR DETAILS =====');
            console.error('[Auth] Error type:', error.constructor.name);
            console.error('[Auth] Error message:', error.message);
            console.error('[Auth] Error stack:', error.stack);
            console.error('[Auth] Full error object:', error);
            
            // Handle network errors with more detail
            if (error.name === 'TimeoutError' || error.message.includes('timeout')) {
                console.error('[Auth] Request timed out - backend may be waking up from sleep');
                throw new Error('Server is taking longer than expected to respond. This may happen if the server is waking up. Please try again in a few seconds.');
            } else if (error instanceof TypeError) {
                console.error('[Auth] TypeError detected - likely network/CORS issue');
                console.error('[Auth] Error message contains "fetch":', error.message.includes('fetch'));
                console.error('[Auth] Error message contains "Failed":', error.message.includes('Failed'));
                // Still throw the generic message for user, but log everything
                throw new Error('Unable to connect to server. The server may be starting up. Please try again in a few moments.');
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
