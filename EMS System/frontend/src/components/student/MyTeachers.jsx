import React, { useState, useEffect } from 'react';
import { studentAPI } from '../../services/api';

const MyTeachers = () => {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTeachers();
  }, []);

  const fetchTeachers = async () => {
    try {
      setLoading(true);
      const data = await studentAPI.getMyTeachers();
      setTeachers(data);
      setError('');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load teachers. Please try again.';
      setError(`Failed to load teachers: ${errorMessage}`);
      console.error('Error fetching teachers:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">Loading teachers...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchTeachers}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm font-medium"
        >
          Retry
        </button>
      </div>
    );
  }

  if (teachers.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-6xl mb-4">👨‍🏫</div>
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">No Teachers Found</h2>
        <p className="text-gray-600">You are not enrolled in any classes yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">My Teachers</h1>
        <button
          onClick={fetchTeachers}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {teachers.map((teacher) => (
          <div key={teacher.id} className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center text-2xl">
                  👨‍🏫
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{teacher.name}</h3>
                  <p className="text-sm text-gray-600">{teacher.email}</p>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Classes:</h4>
              {teacher.classes && teacher.classes.length > 0 ? (
                <div className="space-y-2">
                  {teacher.classes.map((cls) => (
                    <div key={cls.id} className="bg-gray-50 rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{cls.name}</p>
                          <p className="text-sm text-gray-600">
                            {cls.subject_name || 'No Subject'} • Grade {cls.grade}
                          </p>
                        </div>
                      </div>
                      {cls.academic_year && (
                        <p className="text-xs text-gray-500 mt-1">{cls.academic_year}</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No classes assigned</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MyTeachers;

