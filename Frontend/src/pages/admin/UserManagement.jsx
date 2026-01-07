import React, { useState, useEffect } from 'react';
import { FaPlus, FaTrash, FaEdit, FaUserShield, FaChalkboardTeacher, FaUserGraduate, FaUserFriends, FaSearch, FaToggleOn, FaToggleOff } from 'react-icons/fa';
import API_BASE_URL from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import { useModal } from '../../contexts/ModalContext';
import { apiGet, apiPost, apiPut, apiDelete, handleApiError } from '../../utils/apiClient';

const UserManagement = () => {
    const { user: currentUser } = useAuth(); // Rename to avoid conflict
    const { alert, confirm } = useModal();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterRole, setFilterRole] = useState('ALL');

    // Form State
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [editingUserId, setEditingUserId] = useState(null);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
        role: 'STUDENT',
        tenant_id: '' // Will be auto-filled if known, or handled by backend if admin context implies it
    });

    const [adminProfile, setAdminProfile] = useState(null);

    useEffect(() => {
        fetchAdminProfile();
        fetchUsers();
    }, []);

    const fetchAdminProfile = async () => {
        try {
            const token = localStorage.getItem('auth_token');
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setAdminProfile(data);
                // Also set formData tenant_id default
                setFormData(prev => ({ ...prev, tenant_id: data.tenant_id }));
            }
        } catch (error) {
            console.error("Error fetching admin profile:", error);
        }
    };

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const data = await apiGet('/api/v1/ems/users');
            setUsers(data);
        } catch (error) {
            const errorInfo = handleApiError(error, { operation: 'fetch users' });
            await alert(errorInfo.message, errorInfo.title);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = async (e) => {
        e.preventDefault();
        try {
            // Get tenant_id from admin profile or first user
            let tenantId = adminProfile?.tenant_id;
            if (!tenantId && users.length > 0) tenantId = users[0].tenant_id;
            if (!tenantId) {
                // Get default tenant or create one
                const defaultTenant = await apiGet('/api/v1/ems/tenants').catch(() => null);
                if (defaultTenant && defaultTenant.length > 0) {
                    tenantId = defaultTenant[0].id;
                }
            }

            const payload = { ...formData, tenant_id: tenantId || '' };

            await apiPost('/api/v1/ems/users', payload);
            await alert('User created successfully!', 'Success');
            setIsFormOpen(false);
            setFormData({ email: '', password: '', full_name: '', role: 'STUDENT', tenant_id: '' });
            fetchUsers();
        } catch (error) {
            const errorInfo = handleApiError(error, { operation: 'create user' });
            await alert(errorInfo.message, errorInfo.title);
        }
    };

    const handleEditUser = (user) => {
        setFormData({
            email: user.email,
            full_name: user.full_name || '',
            role: user.role,
            password: '', // Don't pre-fill password
            tenant_id: user.tenant_id || ''
        });
        setIsFormOpen(true);
        setEditingUserId(user.id);
    };

    const handleUpdateUser = async (e) => {
        e.preventDefault();
        try {
            if (editingUserId) {
                // Update existing user
                await apiPut(`/api/v1/ems/users/${editingUserId}`, {
                    email: formData.email,
                    full_name: formData.full_name,
                    role: formData.role
                });
                await alert('User updated successfully!', 'Success');
            } else {
                // Create new user
                await handleCreateUser(e);
                return;
            }
            setIsFormOpen(false);
            setEditingUserId(null);
            setFormData({ email: '', password: '', full_name: '', role: 'STUDENT', tenant_id: '' });
            fetchUsers();
        } catch (error) {
            const errorInfo = handleApiError(error, { operation: 'update user' });
            await alert(errorInfo.message, errorInfo.title);
        }
    };

    const handleDeleteUser = async (userId, userName) => {
        const result = await confirm(
            `Are you sure you want to delete ${userName || 'this user'}? This action cannot be undone.`,
            'Delete User'
        );
        if (!result) return;

        try {
            await apiDelete(`/api/v1/ems/users/${userId}`);
            await alert('User deleted successfully!', 'Success');
            fetchUsers();
        } catch (error) {
            const errorInfo = handleApiError(error, { operation: 'delete user' });
            await alert(errorInfo.message, errorInfo.title);
        }
    };

    const handleToggleActive = async (user) => {
        try {
            await apiPut(`/api/v1/ems/users/${user.id}`, {
                is_active: !user.is_active
            });
            await alert(`User ${user.is_active ? 'deactivated' : 'activated'} successfully!`, 'Success');
            fetchUsers();
        } catch (error) {
            const errorInfo = handleApiError(error, { operation: 'toggle user status' });
            await alert(errorInfo.message, errorInfo.title);
        }
    };

    const getRoleIcon = (role) => {
        switch (role) {
            case 'ADMIN': return <FaUserShield className="text-red-400" />;
            case 'TEACHER': return <FaChalkboardTeacher className="text-purple-400" />;
            case 'STUDENT': return <FaUserGraduate className="text-green-400" />;
            case 'PARENT': return <FaUserFriends className="text-orange-400" />;
            default: return <FaUserShield className="text-gray-400" />;
        }
    };

    const filteredUsers = users.filter(u => {
        const matchesSearch = u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            u.email?.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesRole = filterRole === 'ALL' || u.role === filterRole;
        return matchesSearch && matchesRole;
    });

    return (
        <div className="glass-panel p-6 rounded-2xl border border-white/10">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <FaUserFriends className="text-orange-500" />
                    User Management
                </h3>
                        <button
                    onClick={() => {
                        setEditingUserId(null);
                        setFormData({ email: '', password: '', full_name: '', role: 'STUDENT', tenant_id: '' });
                        setIsFormOpen(true);
                    }}
                    className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-500 rounded-lg text-white font-medium transition-colors"
                >
                    <FaPlus className="text-sm" /> Add User
                </button>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-grow">
                    <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search users..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full bg-black/40 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-orange-500"
                    />
                </div>
                <select
                    value={filterRole}
                    onChange={(e) => setFilterRole(e.target.value)}
                    className="bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-orange-500"
                >
                    <option value="ALL">All Roles</option>
                    <option value="STUDENT">Students</option>
                    <option value="TEACHER">Teachers</option>
                    <option value="PARENT">Parents</option>
                    <option value="ADMIN">Admins</option>
                </select>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-white/10 text-gray-400 text-sm uppercase tracking-wider">
                            <th className="py-3 px-4">User</th>
                            <th className="py-3 px-4">Role</th>
                            <th className="py-3 px-4">Email</th>
                            <th className="py-3 px-4">Status</th>
                            <th className="py-3 px-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {loading ? (
                            <tr><td colSpan="5" className="py-8 text-center text-gray-500">Loading users...</td></tr>
                        ) : filteredUsers.length === 0 ? (
                            <tr><td colSpan="5" className="py-8 text-center text-gray-500">No users found.</td></tr>
                        ) : (
                            filteredUsers.map(u => (
                                <tr key={u.id} className="hover:bg-white/5 transition-colors">
                                    <td className="py-3 px-4 font-medium text-white">{u.full_name || 'N/A'}</td>
                                    <td className="py-3 px-4">
                                        <div className="flex items-center gap-2 text-sm">
                                            {getRoleIcon(u.role)}
                                            <span className="capitalize">{u.role.toLowerCase()}</span>
                                        </div>
                                    </td>
                                    <td className="py-3 px-4 text-gray-400 text-sm">{u.email}</td>
                                    <td className="py-3 px-4">
                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${u.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                            {u.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4 text-right">
                                        <div className="flex items-center justify-end gap-2">
                                            <button
                                                onClick={() => handleToggleActive(u)}
                                                className="text-gray-400 hover:text-orange-400 transition-colors p-2"
                                                title={u.is_active ? 'Deactivate' : 'Activate'}
                                            >
                                                {u.is_active ? <FaToggleOn className="text-green-400 text-lg" /> : <FaToggleOff className="text-red-400 text-lg" />}
                                            </button>
                                            <button
                                                onClick={() => handleEditUser(u)}
                                                className="text-gray-400 hover:text-blue-400 transition-colors p-2"
                                                title="Edit"
                                            >
                                                <FaEdit />
                                            </button>
                                            <button
                                                onClick={() => handleDeleteUser(u.id, u.full_name)}
                                                className="text-gray-400 hover:text-red-400 transition-colors p-2"
                                                title="Delete"
                                            >
                                                <FaTrash />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Modal Form */}
            {isFormOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <div className="bg-gray-900 border border-white/10 rounded-2xl w-full max-w-md p-6 relative animate-fade-in-up">
                        <h3 className="text-xl font-bold text-white mb-4">
                            {editingUserId ? 'Edit User' : 'Create New User'}
                        </h3>

                        <form onSubmit={editingUserId ? handleUpdateUser : handleCreateUser} className="space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Full Name</label>
                                <input
                                    type="text" required
                                    value={formData.full_name}
                                    onChange={e => setFormData({ ...formData, full_name: e.target.value })}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-orange-500 outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Email</label>
                                <input
                                    type="email" required
                                    value={formData.email}
                                    onChange={e => setFormData({ ...formData, email: e.target.value })}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-orange-500 outline-none"
                                />
                            </div>
                            {!editingUserId && (
                                <div>
                                    <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Password</label>
                                    <input
                                        type="password" required
                                        value={formData.password}
                                        onChange={e => setFormData({ ...formData, password: e.target.value })}
                                        className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-orange-500 outline-none"
                                    />
                                </div>
                            )}
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Role</label>
                                <select
                                    value={formData.role}
                                    onChange={e => setFormData({ ...formData, role: e.target.value })}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-orange-500 outline-none"
                                >
                                    <option value="STUDENT">Student</option>
                                    <option value="TEACHER">Teacher</option>
                                    <option value="PARENT">Parent</option>
                                    <option value="ADMIN">Admin</option>
                                </select>
                            </div>

                            <div className="flex gap-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setIsFormOpen(false);
                                        setEditingUserId(null);
                                        setFormData({ email: '', password: '', full_name: '', role: 'STUDENT', tenant_id: '' });
                                    }}
                                    className="flex-1 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white font-medium transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 py-2 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-medium transition-colors"
                                >
                                    {editingUserId ? 'Update User' : 'Create User'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserManagement;
