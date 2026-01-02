import React from 'react';
import { Navigate } from 'react-router-dom';
import { getCurrentRole, hasAnyRole } from '../utils/roles';

/**
 * RoleGuard Component
 * Protects routes based on user roles
 */
const RoleGuard = ({ children, allowedRoles = [] }) => {
    const currentRole = getCurrentRole();
    
    // If no roles specified, allow all authenticated users
    if (allowedRoles.length === 0) {
        return children;
    }
    
    // Check if user has required role
    if (!hasAnyRole(allowedRoles)) {
        // Redirect to appropriate dashboard based on role
        const rolePaths = {
            student: '/dashboard',
            teacher: '/teacher/dashboard',
            parent: '/parent/dashboard',
            admin: '/admin/dashboard'
        };
        
        return <Navigate to={rolePaths[currentRole] || '/dashboard'} replace />;
    }
    
    return children;
};

export default RoleGuard;

