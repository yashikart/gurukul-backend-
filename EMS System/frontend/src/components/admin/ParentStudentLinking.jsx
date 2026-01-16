import React, { useState, useEffect } from 'react';
import { schoolAdminAPI } from '../../services/api';

const ParentStudentLinking = () => {
  const [students, setStudents] = useState([]);
  const [parents, setParents] = useState([]);
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [viewMode, setViewMode] = useState('all'); // 'all', 'students', 'parents'

  const [formData, setFormData] = useState({
    student_id: '',
    parent_id: '',
    relationship_type: 'Parent'
  });

  useEffect(() => {
    fetchData();
  }, [viewMode]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [studentsData, parentsData] = await Promise.all([
        schoolAdminAPI.getStudents(),
        schoolAdminAPI.getParents()
      ]);
      setStudents(studentsData);
      setParents(parentsData);
      
      // Fetch links based on view mode
      if (viewMode === 'all') {
        const [studentsWithParents, parentsWithStudents] = await Promise.all([
          schoolAdminAPI.getStudentsWithParents(),
          schoolAdminAPI.getParentsWithStudents()
        ]);
        // Combine the data
        const allLinks = [];
        studentsWithParents.forEach(student => {
          if (student.linked_parents && student.linked_parents.length > 0) {
            student.linked_parents.forEach(parent => {
              allLinks.push({
                id: parent.id || `${student.id}-${parent.id}`,
                student_id: student.id,
                student_name: student.name,
                student_email: student.email,
                parent_id: parent.id,
                parent_name: parent.name,
                parent_email: parent.email,
                relationship_type: parent.relationship_type || 'Parent'
              });
            });
          }
        });
        setLinks(allLinks);
      } else if (viewMode === 'students') {
        const data = await schoolAdminAPI.getStudentsWithParents();
        setLinks(data);
      } else {
        const data = await schoolAdminAPI.getParentsWithStudents();
        setLinks(data);
      }
      setError('');
    } catch (err) {
      setError('Failed to load data. Please try again.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLink = async (e) => {
    e.preventDefault();
    if (!formData.student_id || !formData.parent_id) {
      alert('Please select both student and parent');
      return;
    }
    try {
      await schoolAdminAPI.createParentStudentLink({
        student_id: parseInt(formData.student_id),
        parent_id: parseInt(formData.parent_id),
        relationship_type: formData.relationship_type
      });
      setShowCreateForm(false);
      setFormData({ student_id: '', parent_id: '', relationship_type: 'Parent' });
      fetchData();
      alert('Link created successfully!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create link');
    }
  };

  const handleDeleteLink = async (linkId) => {
    if (!window.confirm('Are you sure you want to delete this link?')) {
      return;
    }
    try {
      await schoolAdminAPI.deleteParentStudentLink(linkId);
      fetchData();
      alert('Link deleted successfully!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete link');
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Parent-Student Linking</h1>
          <p className="text-gray-600 mt-2">Manage relationships between parents and students</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          ➕ Create Link
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* View Mode Selector */}
      <div className="bg-white rounded-lg shadow-md p-4 flex gap-4">
        <button
          onClick={() => setViewMode('all')}
          className={`px-4 py-2 rounded-lg transition ${
            viewMode === 'all'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All Links
        </button>
        <button
          onClick={() => setViewMode('students')}
          className={`px-4 py-2 rounded-lg transition ${
            viewMode === 'students'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Students with Parents
        </button>
        <button
          onClick={() => setViewMode('parents')}
          className={`px-4 py-2 rounded-lg transition ${
            viewMode === 'parents'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Parents with Students
        </button>
      </div>

      {/* Create Link Form */}
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Create Parent-Student Link</h2>
          <form onSubmit={handleCreateLink} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Student *</label>
              <select
                value={formData.student_id}
                onChange={(e) => setFormData({ ...formData, student_id: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Select a student</option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.name} ({student.email}) {student.grade ? `- Grade ${student.grade}` : ''}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Parent *</label>
              <select
                value={formData.parent_id}
                onChange={(e) => setFormData({ ...formData, parent_id: e.target.value })}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Select a parent</option>
                {parents.map((parent) => (
                  <option key={parent.id} value={parent.id}>
                    {parent.name} ({parent.email})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Relationship Type</label>
              <select
                value={formData.relationship_type}
                onChange={(e) => setFormData({ ...formData, relationship_type: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="Parent">Parent</option>
                <option value="Guardian">Guardian</option>
                <option value="Mother">Mother</option>
                <option value="Father">Father</option>
              </select>
            </div>
            <div className="flex gap-3">
              <button
                type="submit"
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                Create Link
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Links List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-xl font-bold text-gray-800">
            {viewMode === 'all' && 'All Links'}
            {viewMode === 'students' && 'Students with Parents'}
            {viewMode === 'parents' && 'Parents with Students'}
          </h2>
        </div>

        {viewMode === 'all' && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-900 uppercase">Student</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-900 uppercase">Parent</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-900 uppercase">Relationship</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-900 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {links.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                      No links found. Create a link to get started.
                    </td>
                  </tr>
                ) : (
                  links.map((link) => (
                    <tr key={link.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-900">
                        <div className="font-medium">{link.student_name}</div>
                        <div className="text-xs text-gray-500">{link.student_email}</div>
                      </td>
                      <td className="px-4 py-3 text-gray-900">
                        <div className="font-medium">{link.parent_name}</div>
                        <div className="text-xs text-gray-500">{link.parent_email}</div>
                      </td>
                      <td className="px-4 py-3 text-gray-900">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {link.relationship_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() => handleDeleteLink(link.id)}
                          className="text-red-600 hover:text-red-800 text-sm font-medium"
                          title="Delete Link"
                        >
                          🗑️ Delete
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {viewMode === 'students' && (
          <div className="divide-y divide-gray-200">
            {links.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">No students with parents found.</div>
            ) : (
              links.map((student) => (
                <div key={student.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{student.name}</h3>
                      <p className="text-sm text-gray-600">{student.email}</p>
                      {student.grade && (
                        <p className="text-xs text-gray-500 mt-1">Grade: {student.grade}</p>
                      )}
                      {student.linked_parents && student.linked_parents.length > 0 && (
                        <div className="mt-3">
                          <p className="text-sm font-medium text-gray-700 mb-2">Linked Parents:</p>
                          <div className="flex flex-wrap gap-2">
                            {student.linked_parents.map((parent, idx) => (
                              <span
                                key={idx}
                                className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded"
                              >
                                {parent.name} ({parent.relationship_type})
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {viewMode === 'parents' && (
          <div className="divide-y divide-gray-200">
            {links.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">No parents with students found.</div>
            ) : (
              links.map((parent) => (
                <div key={parent.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">{parent.name}</h3>
                      <p className="text-sm text-gray-600">{parent.email}</p>
                      {parent.linked_students && parent.linked_students.length > 0 && (
                        <div className="mt-3">
                          <p className="text-sm font-medium text-gray-700 mb-2">Linked Students:</p>
                          <div className="flex flex-wrap gap-2">
                            {parent.linked_students.map((student, idx) => (
                              <span
                                key={idx}
                                className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded"
                              >
                                {student.name} ({student.relationship_type})
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ParentStudentLinking;

