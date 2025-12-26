import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import PrivateRoute from './components/PrivateRoute';
import Dashboard from './pages/Dashboard';
import Subjects from './pages/Subjects';
import Summarizer from './pages/Summarizer';
import Chatbot from './pages/Chatbot';
import Test from './pages/Test';
import AgentSimulator from './pages/AgentSimulator';
import Avatar from './pages/Avatar';
import Settings from './pages/Settings';
import Lectures from './pages/Lectures';
import DraggableAvatar from './components/DraggableAvatar';
import { KarmaProvider } from './contexts/KarmaContext';
import { AuthProvider } from './contexts/AuthContext';
import KarmaNotification from './components/KarmaNotification';
import { SidebarProvider } from './contexts/SidebarContext';
import bgImage from './assets/background.png';

const App = () => {
  // --- Global Timer State Logic (Lifted from Dashboard) ---
  // ... (existing timer logic)

  // (Note: To avoid replacing the whole file repeatedly, just showing the layout part update will affect the import. 
  // But replace_file_content requires contiguous block. I will target the imports and the Route section separately if needed, 
  // or use multi_replace if they are far apart. Here I will replace the imports first then the route using another call or just one replace if I target the App definition start.)

  // Actually, I can just replace the imports block and then the Routes block.
  // Wait, I can't do two replaces in one step unless using multi.
  // I will use multi_replace_file_content.
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
        setTimeLeft(0);
        setIsActive(false);
        setEndTime(null);
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [endTime]);

  // --- Handlers ---
  const handleStartGoal = (durationSeconds) => {
    const newEndTime = Date.now() + (durationSeconds * 1000);
    setTargetGoalSeconds(durationSeconds);
    setEndTime(newEndTime);
  };

  const handleStopGoal = () => {
    setEndTime(null);
    setTargetGoalSeconds(0);
    setTimeLeft(0);
    setIsActive(false);
  };

  return (
    <KarmaProvider>
      <AuthProvider>
        <Router>
          <div className="app-background">
            <img src={bgImage} alt="Gurukul Background" />
            <div className="overlay"></div>
          </div>

          <SidebarProvider>
            <div className="relative z-10 min-h-screen flex flex-col font-sans text-gray-100">
              <Navbar />

              <main className="flex-grow flex flex-col items-center justify-center relative container mx-auto px-2 sm:px-4 mt-16 sm:mt-20">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/signin" element={<SignIn />} />
                  <Route path="/signup" element={<SignUp />} />
                  <Route
                    path="/dashboard"
                    element={
                      <PrivateRoute>
                        <Dashboard
                          studyTimeSeconds={studyTimeSeconds}
                          targetGoalSeconds={targetGoalSeconds}
                          timeLeft={timeLeft}
                          isActive={isActive}
                          onStartGoal={handleStartGoal}
                          onStopGoal={handleStopGoal}
                        />
                      </PrivateRoute>
                    }
                  />
                  <Route path="/subjects" element={<PrivateRoute><Subjects /></PrivateRoute>} />
                  <Route path="/summarizer" element={<PrivateRoute><Summarizer /></PrivateRoute>} />
                  <Route path="/chatbot" element={<PrivateRoute><Chatbot /></PrivateRoute>} />
                  <Route path="/test" element={<PrivateRoute><Test /></PrivateRoute>} />
                  <Route path="/agent-simulator" element={<PrivateRoute><AgentSimulator /></PrivateRoute>} />
                  <Route path="/avatar" element={<PrivateRoute><Avatar /></PrivateRoute>} />
                  <Route path="/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
                  <Route path="/lectures" element={<PrivateRoute><Lectures /></PrivateRoute>} />
                </Routes>
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
        </Router>
      </AuthProvider>
    </KarmaProvider>
  );
};

export default App;
