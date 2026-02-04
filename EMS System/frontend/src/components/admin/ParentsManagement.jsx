import React, { useState, useEffect } from 'react';
import { schoolAdminAPI } from '../../services/api';

const ParentsManagement = () => {
  const [parents, setParents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    student_email: ''
  });
  const [editingParent, setEditingParent] = useState(null);

  useEffect(() => {
    fetchParents();
  }, [searchTerm]);

  const fetchParents = async () => {
    try {
      setLoading(true);
      const data = await schoolAdminAPI.getParents(searchTerm || null);
      setParents(data);
      setError('');
    } catch (err) {
      setError('Failed to load parents. Please try again.');
      console.error('Error fetching parents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateParent = async (e) => {
    e.preventDefault();
    try {
      await schoolAdminAPI.createParent(formData);
      setShowCreateForm(false);
      setFormData({ name: '', email: '', student_email: '' });
      fetchParents();
      alert('Parent created successfully! Login credentials sent via email.');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create parent');
    }
  };

  const handleEdit = (parent) => {
    setEditingParent(parent);
    setFormData({
      name: parent.name,
      email: parent.email,
      student_email: ''
    });
    setShowCreateForm(true);
  };

  const handleUpdateParent = async (e) => {
    e.preventDefault();
    try {
      await schoolAdminAPI.updateParent(editingParent.id, {
        name: formData.name,
        email: formData.email
      });
      setShowCreateForm(false);
      setEditingParent(null);
      setFormData({ name: '', email: '', student_email: '' });
      fetchParents();
      alert('Parent updated successfully!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update parent');
    }
  };

  const handleDelete = async (parentId) => {
    if (!window.confirm('Are you sure you want to delete this parent? This action cannot be undone.')) {
      return;
    }
    try {
      await schoolAdminAPI.deleteParent(parentId);
      fetchParents();
      alert('Parent deleted successfully!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete parent');
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">Loading parents...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-xl md:text-3xl font-bold text-gray-800">Parents Management</h1>
          <p className="text-sm md:text-base text-gray-600 mt-1 md:mt-2">Manage all parents in your school</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="px-3 md:px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm md:text-base whitespace-nowrap"
          >
            ➕ Add Parent
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-4">
        <input
          type="text"
          placeholder="Search parents by name or email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            {editingParent ? 'Edit Parent' : 'Create New Parent'}
          </h2>
          <form onSubmit={editingParent ? handleUpdateParent : handleCreateParent} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            {!editingParent && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Student Email</label>
                <input
                  type="email"
                  value={formData.student_email}
                  onChange={(e) => setFormData({ ...formData, student_email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="Optional: Link to existing student"
                />
              </div>
            )}
            <div className="flex gap-3">
              <button
                type="submit"
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                {editingParent ? 'Update Parent' : 'Create Parent'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingParent(null);
                  setFormData({ name: '', email: '', student_email: '' });
                }}
                className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">All Parents ({parents.length})</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {parents.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                    No parents found
                  </td>
                </tr>
              ) : (
                parents.map((parent) => (
                  <tr key={parent.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{parent.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{parent.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{parent.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEdit(parent)}
                          className="text-indigo-600 hover:text-indigo-900 transition"
                          title="Edit"
                        >
                          ✏️ Edit
                        </button>
                        <button
                          onClick={() => handleDelete(parent.id)}
                          className="text-red-600 hover:text-red-900 transition"
                          title="Delete"
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ParentsManagement;
