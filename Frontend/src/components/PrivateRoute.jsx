import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const PrivateRoute = ({ children }) => {
    const { user, loading } = useAuth();

    // Show a loading spinner or nothing while checking auth status
    if (loading) {
        return <div className="min-h-screen flex items-center justify-center text-white">Loading...</div>;
    }

    // If not logged in, redirect to login page
    if (!user) {
        return <Navigate to="/signin" />;
    }

    // If logged in, render the protected component
    return children;
};

export default PrivateRoute;
