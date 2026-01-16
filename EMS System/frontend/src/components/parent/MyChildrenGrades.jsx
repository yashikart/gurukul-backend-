import React, { useState, useEffect } from 'react';
import { parentAPI } from '../../services/api';

const MyChildrenGrades = () => {
  const [children, setChildren] = useState([]);
  const [selectedChildId, setSelectedChildId] = useState('');
  const [grades, setGrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchChildren();
  }, []);

  useEffect(() => {
    if (selectedChildId) {
      fetchGrades(selectedChildId);
    }
  }, [selectedChildId]);

  const fetchChildren = async () => {
    try {
      const data = await parentAPI.getMyChildren();
      setChildren(data);
      if (data.length > 0) {
        setSelectedChildId(data[0].id.toString());
      } else {
        setLoading(false);
      }
    } catch (err) {
      setError('Failed to load children.');
      console.error('Error fetching children:', err);
      setLoading(false);
    }
  };

  const fetchGrades = async (childId) => {
    try {
      setLoading(true);
      const childIdInt = childId ? parseInt(childId, 10) : null;
      const data = await parentAPI.getMyChildrenGrades(childIdInt);
      setGrades(data || []);
      setError('');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load grades. Please try again.';
      setError(errorMessage);
      console.error('Error fetching grades:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && children.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">Loading grades...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Children's Grades</h1>
          <p className="text-gray-600 mt-2">View grades for your children</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Child Filter */}
      {children.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4 flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Child
            </label>
            <select
              value={selectedChildId}
              onChange={(e) => setSelectedChildId(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Children</option>
              {children.map((child) => (
                <option key={child.id} value={child.id.toString()}>
                  {child.name} {child.grade ? `(Grade ${child.grade})` : ''}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Grades Display */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-xl font-bold text-gray-800">Grades</h2>
        </div>
        {grades.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <p className="text-gray-500 text-lg">No grades available yet.</p>
            <p className="text-gray-400 text-sm mt-2">Grades will appear here once they are recorded by teachers.</p>
          </div>
        ) : (
          <div className="p-6">
            <p className="text-gray-600">Grades feature coming soon. Check back later!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyChildrenGrades;

