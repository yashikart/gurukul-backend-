import React, { useState, useEffect } from 'react';
import { FaPlus, FaTrash, FaUserShield, FaChalkboardTeacher, FaUserGraduate, FaUserFriends, FaSearch } from 'react-icons/fa';
import API_BASE_URL from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import { useModal } from '../../contexts/ModalContext';

const UserManagement = () => {
    const { user: currentUser } = useAuth(); // Rename to avoid conflict
    const { alert, confirm } = useModal();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterRole, setFilterRole] = useState('ALL');

    // Form State
    const [isFormOpen, setIsFormOpen] = useState(false);
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
            const token = localStorage.getItem('token');
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
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/v1/ems/users`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setUsers(data);
            } else {
                console.error("Failed to fetch users");
            }
        } catch (error) {
            console.error("Error fetching users:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            // Assuming current admin's tenant ID is available or backend handles it.
            // But API expects tenant_id. Let's try to get it from current user or fetch it first.
            // For MVP, if backend enforces tenant_id in schema, we need it. 
            // In a real app, Admin creates user in THEIR tenant unless SuperAdmin.
            // Let's assume backend `create_user_within_tenant` requires `tenant_id`.
            // Ideally backend should default to current_user.tenant_id if payload is missing it?
            // Checking ems.py... Schema `UserCreateAdmin` has `tenant_id`.
            // We need to fetch the admin's profile first to get tenant_id? Or just decode the token?
            // Hack: We will fetch the user list first, grab the first tenant_id we see and use that :D 
            // Better: User object in AuthContext likely has it.

            // Use fetched admin profile tenant_id, or fallback to first user, or worst case dummy
            let tenantId = adminProfile?.tenant_id;
            if (!tenantId && users.length > 0) tenantId = users[0].tenant_id;

            console.log("Creating user with Tenant ID:", tenantId); // Debug

            const payload = { ...formData, tenant_id: tenantId };

            const response = await fetch(`${API_BASE_URL}/api/v1/ems/users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                await alert('User created successfully!', 'Success');
                setIsFormOpen(false);
                setFormData({ email: '', password: '', full_name: '', role: 'STUDENT', tenant_id: '' });
                fetchUsers();
            } else {
                const err = await response.json();
                await alert(`Failed to create user: ${err.detail}`, 'Error');
            }
        } catch (error) {
            console.error("Error creating user:", error);
            await alert('An error occurred.', 'Error');
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
                    onClick={() => setIsFormOpen(true)}
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
                            {/* <th className="py-3 px-4 text-right">Actions</th> */}
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
                                    {/* <td className="py-3 px-4 text-right">
                                        <button className="text-gray-400 hover:text-red-400 transition-colors p-2"><FaTrash /></button>
                                    </td> */}
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
                        <h3 className="text-xl font-bold text-white mb-4">Create New User</h3>

                        <form onSubmit={handleCreateUser} className="space-y-4">
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
                            <div>
                                <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Password</label>
                                <input
                                    type="password" required
                                    value={formData.password}
                                    onChange={e => setFormData({ ...formData, password: e.target.value })}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-orange-500 outline-none"
                                />
                            </div>
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
                                    onClick={() => setIsFormOpen(false)}
                                    className="flex-1 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white font-medium transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 py-2 rounded-lg bg-orange-600 hover:bg-orange-500 text-white font-medium transition-colors"
                                >
                                    Create User
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
