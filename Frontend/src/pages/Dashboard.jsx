import React from 'react';
import Sidebar from '../components/Sidebar';
import { StudyTimeWidget, KarmaWidget, AchievementsWidget, GoalWidget } from '../components/DashboardWidgets';
import LearningFlow from '../components/LearningFlow';
import LearningProgress from '../components/LearningProgress';

const Dashboard = ({
    studyTimeSeconds,
    targetGoalSeconds,
    timeLeft,
    isActive,
    onStartGoal,
    onStopGoal
}) => {
    // Internal state moved to App.jsx for global persistence

    return (
        <div className="flex pt-20 sm:pt-24 min-h-screen container mx-auto px-2 sm:px-4 gap-3 sm:gap-6">
            {/* Left Sidebar */}
            <Sidebar />

            {/* Main Content Area */}
            <main className="flex-grow animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <div className="mb-4 sm:mb-8">
                    <h2 className="text-2xl sm:text-3xl font-bold font-heading text-white">Dashboard</h2>
                    <p className="text-gray-200 text-xs sm:text-sm font-medium notranslate">
                        {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    </p>
                </div>

                {/* Learning Flow - Guided Journey */}
                <div className="mb-6 sm:mb-8">
                    <LearningFlow currentStep="improve" />
                </div>

                {/* Improved Grid Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
                    {/* Column 1 & 2 */}
                    <div className="lg:col-span-2 flex flex-col gap-4 sm:gap-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                            <StudyTimeWidget
                                targetGoalSeconds={targetGoalSeconds}
                                timeLeft={timeLeft}
                                isActive={isActive}
                                totalStudyTime={studyTimeSeconds}
                            />
                            <KarmaWidget />
                        </div>
                        <GoalWidget
                            timeLeft={timeLeft}
                            isActive={isActive}
                            onStart={onStartGoal}
                            onStop={onStopGoal}
                        />
                    </div>

                    {/* Column 3 */}
                    <div className="flex flex-col gap-4 sm:gap-6">
                        <LearningProgress />
                        <AchievementsWidget />
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
