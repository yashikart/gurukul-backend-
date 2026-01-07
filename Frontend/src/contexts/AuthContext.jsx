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

    // Check if user is authenticated on mount
    useEffect(() => {
        const checkAuth = async () => {
            const storedToken = localStorage.getItem('auth_token');
            if (storedToken) {
                try {
                    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
                        headers: {
                            'Authorization': `Bearer ${storedToken}`
                        }
                    });
                    
                    if (response.ok) {
                        const userData = await response.json();
                        setUser({
                            id: userData.id,
                            email: userData.email,
                            full_name: userData.full_name,
                            role: userData.role
                        });
                    } else {
                        // Token is invalid, clear it
                        localStorage.removeItem('auth_token');
                        setToken(null);
                        setUser(null);
                    }
                } catch (error) {
                    console.error('Auth check failed:', error);
                    localStorage.removeItem('auth_token');
                    setToken(null);
                    setUser(null);
                }
            }
            setLoading(false);
        };
        
        checkAuth();
    }, []);

    const login = async (email, password) => {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        
        // Store token
        localStorage.setItem('auth_token', data.access_token);
        setToken(data.access_token);
        
        // Set user
        setUser(data.user);
        
        return { session: { access_token: data.access_token }, user: data.user };
    };

    const signup = async (email, password, role, full_name) => {
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

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        const data = await response.json();
        
        // Store token
        localStorage.setItem('auth_token', data.access_token);
        setToken(data.access_token);
        
        // Set user
        setUser(data.user);
        
        return { user: data.user, session: { access_token: data.access_token } };
    };

    const logout = async () => {
        // Clear token and user
        localStorage.removeItem('auth_token');
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
