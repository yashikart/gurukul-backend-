import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import emsApi from '../../services/emsApi';
import { handleApiError } from '../../utils/apiClient';
import { FaGraduationCap, FaSpinner, FaRedo, FaBookOpen } from 'react-icons/fa';
import EMSAuthentication from '../../components/EMSAuthentication';

const MyGrades = () => {
    const { user } = useAuth();
    const [grades, setGrades] = useState([]);
    const [classes, setClasses] = useState([]);
    const [selectedClassId, setSelectedClassId] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [emsToken, setEmsToken] = useState(null);
    const [showAuth, setShowAuth] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('ems_token');
        if (token) {
            setEmsToken(token);
            fetchClasses(token);
        } else {
            setShowAuth(true);
            setLoading(false);
        }
    }, []);

    const handleAuthSuccess = (token) => {
        setEmsToken(token);
        setShowAuth(false);
        fetchClasses(token);
    };

    useEffect(() => {
        if (emsToken && selectedClassId) {
            fetchGrades(selectedClassId);
        } else if (emsToken && selectedClassId === '' && classes.length > 0) {
            // If "All Classes" is selected, don't fetch (grades endpoint might not support it)
            setGrades([]);
        }
    }, [selectedClassId, emsToken]);

    const fetchClasses = async (token) => {
        try {
            const data = await emsApi.getClasses(token);
            setClasses(data || []);
            if (data && data.length > 0) {
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
            const classIdInt = classId ? parseInt(classId, 10) : null;
            const data = await emsApi.getGrades(emsToken, classIdInt);
            setGrades(data || []);
            setError('');
        } catch (err) {
            const errorInfo = handleApiError(err, { context: 'Loading grades' });
            setError(errorInfo.message || 'Failed to load grades');
            console.error('Error fetching grades:', err);
        } finally {
            setLoading(false);
        }
    };

    if (showAuth) {
        return <EMSAuthentication onSuccess={handleAuthSuccess} onCancel={() => setShowAuth(false)} />;
    }

    if (loading && grades.length === 0 && classes.length === 0) {
        return (
            <div className="flex pt-20 sm:pt-24 min-h-screen container mx-auto px-2 sm:px-4 justify-center items-center">
                <div className="text-center">
                    <FaSpinner className="animate-spin text-4xl text-orange-400 mx-auto mb-4" />
                    <p className="text-gray-300 text-lg">Loading grades...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex pt-20 sm:pt-24 min-h-screen container mx-auto px-2 sm:px-4 gap-3 sm:gap-6 pb-20">
            <div className="w-full max-w-7xl mx-auto">
                <div className="mb-6 sm:mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h2 className="text-2xl sm:text-3xl font-bold font-heading text-white flex items-center gap-3">
                            <FaGraduationCap className="text-orange-400" />
                            My Grades
                        </h2>
                        <p className="text-gray-200 text-xs sm:text-sm font-medium mt-2">
                            View your academic performance and grades
                        </p>
                    </div>
                    {emsToken && (
                        <button
                            onClick={() => selectedClassId && fetchGrades(selectedClassId)}
                            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white rounded-xl font-medium shadow-lg transition-transform hover:-translate-y-1"
                        >
                            <FaRedo className="text-sm" />
                            <span>Refresh</span>
                        </button>
                    )}
                </div>

                {error && (
                    <div className="mb-6 glass-panel border border-red-500/30 bg-red-500/10 p-4 rounded-xl">
                        <p className="text-red-300 text-sm">{error}</p>
                    </div>
                )}

                {/* Class Filter */}
                {classes.length > 0 && (
                    <div className="glass-panel p-4 border border-white/10 rounded-2xl mb-6 bg-black/40">
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Filter by Class
                        </label>
                        <select
                            value={selectedClassId}
                            onChange={(e) => setSelectedClassId(e.target.value)}
                            className="w-full px-4 py-2 bg-black/60 border border-white/20 rounded-xl text-white focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition"
                        >
                            <option value="">All Classes</option>
                            {classes.map((cls) => (
                                <option key={cls.id} value={cls.id.toString()} className="bg-black text-white">
                                    {cls.name} {cls.subject_name ? `(${cls.subject_name})` : ''}
                                </option>
                            ))}
                        </select>
                    </div>
                )}

                {/* Grades Display */}
                <div className="glass-panel border border-white/10 rounded-2xl overflow-hidden bg-black/40">
                    <div className="px-4 sm:px-6 py-4 border-b border-white/10 bg-white/5">
                        <h3 className="text-xl font-bold text-white">Grades</h3>
                    </div>
                    {loading ? (
                        <div className="p-12 text-center">
                            <FaSpinner className="animate-spin text-3xl text-orange-400 mx-auto mb-4" />
                            <p className="text-gray-300">Loading grades...</p>
                        </div>
                    ) : grades.length === 0 ? (
                        <div className="px-6 py-12 text-center">
                            <FaGraduationCap className="text-5xl text-gray-400 mx-auto mb-4 opacity-50" />
                            <p className="text-gray-300 text-lg">No grades available yet.</p>
                            <p className="text-gray-400 text-sm mt-2">
                                Your grades will appear here once they are recorded by your teachers.
                            </p>
                        </div>
                    ) : (
                        <div className="p-6">
                            <p className="text-gray-300">
                                Grades feature is ready. Detailed grade display will be implemented when grades are available in the system.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MyGrades;

