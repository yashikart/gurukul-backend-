import React, { useState, useEffect } from 'react';
import { teacherAPI } from '../../services/api';

const MyTimetable = () => {
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  useEffect(() => {
    fetchTimetable();
  }, []);

  const fetchTimetable = async () => {
    try {
      setLoading(true);
      const data = await teacherAPI.getMyTimetable();
      setSlots(data);
      setError('');
    } catch (err) {
      setError('Failed to load timetable. Please try again.');
      console.error('Error fetching timetable:', err);
    } finally {
      setLoading(false);
    }
  };

  // Group slots by day
  const groupedSlots = {};
  daysOfWeek.forEach((day, index) => {
    groupedSlots[index] = slots.filter(slot => slot.day_of_week === index);
  });

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">Loading timetable...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">My Timetable</h1>
          <p className="text-gray-600 mt-2">View your weekly class schedule</p>
        </div>
        <button
          onClick={fetchTimetable}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {slots.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <p className="text-gray-600">No timetable slots assigned yet.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Day</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Class</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Subject</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase">Room</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {daysOfWeek.map((day, dayIndex) => {
                  const daySlots = groupedSlots[dayIndex] || [];
                  if (daySlots.length === 0) {
                    return (
                      <tr key={dayIndex} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{day}</td>
                        <td colSpan="4" className="px-6 py-4 text-sm text-gray-500">No classes scheduled</td>
                      </tr>
                    );
                  }
                  return daySlots.map((slot, slotIndex) => (
                    <tr key={`${dayIndex}-${slotIndex}`} className="hover:bg-gray-50">
                      {slotIndex === 0 && (
                        <td
                          rowSpan={daySlots.length}
                          className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 align-top"
                        >
                          {day}
                        </td>
                      )}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {slot.start_time} - {slot.end_time}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {slot.class_name || `Class #${slot.class_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {slot.subject_name || `Subject #${slot.subject_id}`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {slot.room || '-'}
                      </td>
                    </tr>
                  ));
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyTimetable;

