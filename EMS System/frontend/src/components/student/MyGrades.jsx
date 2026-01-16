import React, { useState, useEffect } from 'react';
import { studentAPI } from '../../services/api';

const MyGrades = () => {
  const [grades, setGrades] = useState([]);
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchClasses();
  }, []);

  useEffect(() => {
    if (selectedClassId) {
      fetchGrades(selectedClassId);
    }
  }, [selectedClassId]);

  const fetchClasses = async () => {
    try {
      const data = await studentAPI.getMyClasses();
      setClasses(data);
      if (data.length > 0) {
        setSelectedClassId(data[0].id.toString());
      } else {
        setLoading(false);
      }
    } catch (err) {
      setError('Failed to load classes.');
      console.error('Error fetching classes:', err);
      setLoading(false);
    }
  };

  const fetchGrades = async (classId) => {
    try {
      setLoading(true);
      const data = await studentAPI.getMyGrades(classId || null);
      setGrades(data || []);
      setError('');
    } catch (err) {
      setError('Failed to load grades. Please try again.');
      console.error('Error fetching grades:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
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
          <h1 className="text-3xl font-bold text-gray-800">My Grades</h1>
          <p className="text-gray-600 mt-2">View your academic performance and grades</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Class Filter */}
      {classes.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4 flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Class
            </label>
            <select
              value={selectedClassId}
              onChange={(e) => setSelectedClassId(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Classes</option>
              {classes.map((cls) => (
                <option key={cls.id} value={cls.id}>
                  {cls.name} {cls.subject_name ? `(${cls.subject_name})` : ''}
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
            <p className="text-gray-400 text-sm mt-2">Your grades will appear here once they are recorded by your teachers.</p>
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

export default MyGrades;

