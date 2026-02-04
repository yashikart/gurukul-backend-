import React, { Suspense } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import KarmaNotification from './components/KarmaNotification';
import Home from './pages/Home';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import PrivateRoute from './components/PrivateRoute';
import ErrorBoundary from './components/ErrorBoundary';
import NotFound from './pages/NotFound';
import RoleGuard from './components/RoleGuard';
import Subjects from './pages/Subjects';
import Avatar from './pages/Avatar';
import Settings from './pages/Settings';
import MyContent from './pages/MyContent';
import DraggableAvatar from './components/DraggableAvatar';

// Lazy load heavy pages for code splitting
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const AdminDashboard = React.lazy(() => import('./pages/admin/AdminDashboard'));
const TeacherDashboard = React.lazy(() => import('./pages/teacher/TeacherDashboard'));
const ParentDashboard = React.lazy(() => import('./pages/parent/ParentDashboard'));
const Summarizer = React.lazy(() => import('./pages/Summarizer'));
const Chatbot = React.lazy(() => import('./pages/Chatbot'));
const Test = React.lazy(() => import('./pages/Test'));
const AgentSimulator = React.lazy(() => import('./pages/AgentSimulator'));
const Lectures = React.lazy(() => import('./pages/Lectures'));
const Flashcards = React.lazy(() => import('./pages/Flashcards'));
const MyClasses = React.lazy(() => import('./pages/ems/MyClasses'));
const MySchedule = React.lazy(() => import('./pages/ems/MySchedule'));
const MyAnnouncements = React.lazy(() => import('./pages/ems/MyAnnouncements'));
const MyAttendance = React.lazy(() => import('./pages/ems/MyAttendance'));
const MyTeachers = React.lazy(() => import('./pages/ems/MyTeachers'));

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[calc(100vh-200px)]">
    <div className="text-center">
      <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent mb-4"></div>
      <p className="text-gray-400">Loading...</p>
    </div>
  </div>
);
import { KarmaProvider, useKarma } from './contexts/KarmaContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ModalProvider } from './contexts/ModalContext';
import { PranaProvider } from './contexts/PranaContext';
import { SidebarProvider } from './contexts/SidebarContext';
import { sendLifeEvent } from './utils/karmaTrackerClient';
import bgImage from './assets/background.png';

const AppContent = () => {
  const { user } = useAuth();
  const { refreshKarma } = useKarma();

  // --- Global Timer State Logic (Lifted from Dashboard) ---
  // Total Study Time (Persists only for the current day)
  const [studyTimeSeconds, setStudyTimeSeconds] = React.useState(() => {
    const saved = localStorage.getItem('gurukul_studyTime');
    const savedDate = localStorage.getItem('gurukul_studyDate');
    const today = new Date().toDateString();

    if (savedDate !== today) {
      return 0; // Reset if new day
    }
    return saved ? parseInt(saved, 10) : 0;
  });

  // Target Goal Duration
  const [targetGoalSeconds, setTargetGoalSeconds] = React.useState(() => {
    const saved = localStorage.getItem('gurukul_targetGoal');
    return saved ? parseInt(saved, 10) : 0;
  });

  // Goal End Timestamp
  const [endTime, setEndTime] = React.useState(() => {
    const saved = localStorage.getItem('gurukul_goalEndTime');
    return saved ? parseInt(saved, 10) : null;
  });

  // Derived State for Goal Timer
  const [timeLeft, setTimeLeft] = React.useState(0);
  const [isActive, setIsActive] = React.useState(false);
  
  // Track previous timeLeft to detect completion
  const prevTimeLeftRef = React.useRef(0);
  const goalCompletedRef = React.useRef(false);

  // --- Persistence Effects ---
  React.useEffect(() => {
    localStorage.setItem('gurukul_studyTime', studyTimeSeconds);
    localStorage.setItem('gurukul_studyDate', new Date().toDateString());
  }, [studyTimeSeconds]);

  React.useEffect(() => {
    localStorage.setItem('gurukul_targetGoal', targetGoalSeconds);
  }, [targetGoalSeconds]);

  React.useEffect(() => {
    if (endTime) {
      localStorage.setItem('gurukul_goalEndTime', endTime);
    } else {
      localStorage.removeItem('gurukul_goalEndTime');
    }
  }, [endTime]);

  // --- Timer Intervals ---
  // Study Time Ticker - Runs continuously globally
  React.useEffect(() => {
    const interval = setInterval(() => {
      setStudyTimeSeconds(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Goal Timer Sync
  React.useEffect(() => {
    if (!endTime) {
      setTimeLeft(0);
      setIsActive(false);
      return;
    }

    const updateTimer = () => {
      const now = Date.now();
      const remaining = Math.ceil((endTime - now) / 1000);

      if (remaining > 0) {
        setTimeLeft(remaining);
        setIsActive(true);
      } else {
        // Timer completed naturally - mark as completed before clearing
        goalCompletedRef.current = true;
        const completedDuration = targetGoalSeconds;
        
        setTimeLeft(0);
        setIsActive(false);
        setEndTime(null);
        
        // Award karma for completing daily goal
        if (user?.id) {
          sendLifeEvent({
            userId: user.id,
            action: 'completing_lessons',
            role: 'learner',
            note: `Completed daily goal timer (${Math.floor(completedDuration / 60)} minutes)`,
            context: `source=daily_goal_timer;duration=${completedDuration}`
          }).then(() => {
            // Refresh karma after a short delay to allow backend to process
            setTimeout(() => {
              refreshKarma?.();
            }, 500);
          }).catch(err => {
            console.warn('[Karma] Failed to log goal completion:', err);
          });
        }
        
        goalCompletedRef.current = false; // Reset flag after sending event
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [endTime, targetGoalSeconds, user]);

  // --- Handlers ---
  const handleStartGoal = (durationSeconds) => {
    const newEndTime = Date.now() + (durationSeconds * 1000);
    setTargetGoalSeconds(durationSeconds);
    setEndTime(newEndTime);
    goalCompletedRef.current = false; // Reset completion flag when starting new goal
  };

  const handleStopGoal = () => {
    // Capture values BEFORE resetting state (important: React state updates are async)
    const currentTimeLeft = timeLeft;
    const goalDuration = targetGoalSeconds;
    const wasPremature = isActive && currentTimeLeft > 0; // Timer was active and had time remaining
    
    // Reset state
    setEndTime(null);
    setTargetGoalSeconds(0);
    setTimeLeft(0);
    setIsActive(false);
    goalCompletedRef.current = false; // Reset completion flag
    
    // Subtract karma for premature stop
    if (wasPremature && user?.id && goalDuration > 0) {
      const minutesLeft = Math.floor(currentTimeLeft / 60);
      const totalMinutes = Math.floor(goalDuration / 60);
      
      console.log('[Karma] Premature stop detected:', { 
        currentTimeLeft, 
        goalDuration, 
        minutesLeft, 
        totalMinutes,
        userId: user.id,
        isActive,
        wasPremature
      });
      
      sendLifeEvent({
        userId: user.id,
        action: 'cheat',
        role: 'learner',
        note: `Stopped daily goal timer prematurely (${minutesLeft} minutes remaining of ${totalMinutes} minute goal)`,
        context: `source=daily_goal_timer;premature_stop=true;time_left=${currentTimeLeft};goal_duration=${goalDuration}`
      }).then((response) => {
        console.log('[Karma] Premature stop event sent successfully:', response);
        // Refresh karma after a short delay to allow backend to process
        setTimeout(() => {
          console.log('[Karma] Refreshing karma after premature stop...');
          refreshKarma?.();
        }, 1000); // Increased delay to 1 second to ensure backend processing
      }).catch(err => {
        console.error('[Karma] Failed to log premature stop:', err);
      });
    } else {
      console.log('[Karma] Stop was not premature:', { 
        wasPremature, 
        isActive, 
        currentTimeLeft, 
        goalDuration, 
        hasUser: !!user?.id 
      });
    }
  };

  return (
    <Router>
      <div className="app-background">
        <img src={bgImage} alt="Gurukul Background" loading="lazy" />
        <div className="overlay"></div>
      </div>

      <ModalProvider>
        <SidebarProvider>
          <div className="relative z-10 min-h-screen flex flex-col font-sans text-gray-100">
            <Navbar />

            <main className="flex-grow flex flex-col items-center justify-center relative container mx-auto px-2 sm:px-4 mt-16 sm:mt-20">
              <ErrorBoundary>
                <Suspense fallback={<PageLoader />}>
                  <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/signin" element={<SignIn />} />
                  <Route path="/signup" element={<SignUp />} />
                  <Route
                    path="/dashboard"
                    element={
                      <PrivateRoute>
                        <RoleGuard allowedRoles={['student']}>
                          <Dashboard
                            studyTimeSeconds={studyTimeSeconds}
                            targetGoalSeconds={targetGoalSeconds}
                            timeLeft={timeLeft}
                            isActive={isActive}
                            onStartGoal={handleStartGoal}
                            onStopGoal={handleStopGoal}
                          />
                        </RoleGuard>
                      </PrivateRoute>
                    }
                  />
                          <Route path="/subjects" element={<PrivateRoute><Subjects /></PrivateRoute>} />
                          <Route path="/summarizer" element={<PrivateRoute><Summarizer /></PrivateRoute>} />
                          <Route path="/chatbot" element={<PrivateRoute><Chatbot /></PrivateRoute>} />
                          <Route path="/test" element={<PrivateRoute><Test /></PrivateRoute>} />
                          <Route path="/flashcards" element={<PrivateRoute><Flashcards /></PrivateRoute>} />
                          <Route path="/agent-simulator" element={<PrivateRoute><AgentSimulator /></PrivateRoute>} />
                          <Route path="/agent-simulator/:agentName" element={<PrivateRoute><AgentSimulator /></PrivateRoute>} />
                          <Route path="/avatar" element={<PrivateRoute><Avatar /></PrivateRoute>} />
                          <Route path="/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
                          <Route path="/lectures" element={<PrivateRoute><Lectures /></PrivateRoute>} />
                          <Route path="/my-content" element={<PrivateRoute><RoleGuard allowedRoles={['student']}><MyContent /></RoleGuard></PrivateRoute>} />

                          {/* EMS Student Routes */}
                          <Route
                            path="/ems/classes"
                            element={
                              <PrivateRoute>
                                <RoleGuard allowedRoles={['student']}>
                                  <MyClasses />
                                </RoleGuard>
                              </PrivateRoute>
                            }
                          />
                          <Route
                            path="/ems/schedule"
                            element={
                              <PrivateRoute>
                                <RoleGuard allowedRoles={['student']}>
                                  <MySchedule />
                                </RoleGuard>
                              </PrivateRoute>
                            }
                          />
                          <Route
                            path="/ems/announcements"
                            element={
                              <PrivateRoute>
                                <RoleGuard allowedRoles={['student']}>
                                  <MyAnnouncements />
                                </RoleGuard>
                              </PrivateRoute>
                            }
                          />
                          <Route
                            path="/ems/attendance"
                            element={
                              <PrivateRoute>
                                <RoleGuard allowedRoles={['student']}>
                                  <MyAttendance />
                                </RoleGuard>
                              </PrivateRoute>
                            }
                          />
                          <Route
                            path="/ems/teachers"
                            element={
                              <PrivateRoute>
                                <RoleGuard allowedRoles={['student']}>
                                  <MyTeachers />
                                </RoleGuard>
                              </PrivateRoute>
                            }
                          />

                          {/* EMS + Governance Routes */}
                          <Route
                            path="/admin_dashboard"
                            element={
                              <PrivateRoute>
                                <RoleGuard allowedRoles={['admin']}>
                                  <AdminDashboard />
                                </RoleGuard>
                              </PrivateRoute>
                            }
                          />
                          <Route
                            path="/teacher/dashboard"
                            element={
                              <PrivateRoute>
                                <RoleGuard allowedRoles={['teacher']}>
                                  <TeacherDashboard />
                                </RoleGuard>
                              </PrivateRoute>
                            }
                          />
                          <Route
                            path="/parent/dashboard"
                            element={
                              <PrivateRoute>
                                <RoleGuard allowedRoles={['parent']}>
                                  <ParentDashboard />
                                </RoleGuard>
                              </PrivateRoute>
                            }
                          />

                          {/* 404 Route - Catch all unmatched routes */}
                          <Route path="*" element={<NotFound />} />
                        </Routes>
                      </Suspense>
                      </ErrorBoundary>
                    </main>

                    {/* Draggable Avatar - appears on all pages when image is uploaded */}
                    <DraggableAvatar />

                    {/* Karma Notifications */}
                    <KarmaNotification />

                    <footer className="text-center py-4 sm:py-6 text-xs sm:text-sm text-gray-500 relative z-10 px-4">
                      <p>© 2024 Gurukul. All rights reserved.</p>
                    </footer>
                  </div>
                </SidebarProvider>
              </ModalProvider>
            </Router>
  );
};

const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <KarmaProvider>
          <PranaProvider>
            <AppContent />
          </PranaProvider>
        </KarmaProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
