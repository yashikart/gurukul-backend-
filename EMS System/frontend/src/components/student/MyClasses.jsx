import React, { useState, useEffect } from 'react';
import { studentAPI } from '../../services/api';

const MyClasses = () => {
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchClasses();
  }, []);

  const fetchClasses = async () => {
    try {
      setLoading(true);
      const data = await studentAPI.getMyClasses();
      setClasses(data);
      setError('');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load classes. Please try again.';
      setError(`Failed to load classes: ${errorMessage}`);
      console.error('Error fetching classes:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">Loading classes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchClasses}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm font-medium"
        >
          Retry
        </button>
      </div>
    );
  }

  if (classes.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">📚</div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">No Classes Found</h2>
        <p className="text-gray-600">You are not enrolled in any classes yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">My Classes</h1>
        <button
          onClick={fetchClasses}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((cls) => (
          <div key={cls.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-1">{cls.name}</h3>
                <p className="text-sm text-gray-600">Grade {cls.grade}</p>
              </div>
              <div className="text-3xl">📚</div>
            </div>

            <div className="space-y-3 pt-4 border-t border-gray-200">
              <div className="flex items-center text-sm">
                <span className="font-medium text-gray-700 w-20">Subject:</span>
                <span className="text-gray-900">{cls.subject_name || 'N/A'}</span>
              </div>
              <div className="flex items-center text-sm">
                <span className="font-medium text-gray-700 w-20">Teacher:</span>
                <span className="text-gray-900">{cls.teacher_name || 'N/A'}</span>
              </div>
              {cls.academic_year && (
                <div className="flex items-center text-sm">
                  <span className="font-medium text-gray-700 w-20">Year:</span>
                  <span className="text-gray-900">{cls.academic_year}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MyClasses;

