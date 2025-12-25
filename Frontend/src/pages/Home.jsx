import React from 'react';
import Hero from '../components/Hero';
import FeatureGrid from '../components/FeatureGrid';

const Home = () => {
    return (
        <div className="flex flex-col items-center justify-center min-h-[calc(100vh-80px)] w-full">
            <Hero />
            <div className="mt-16 w-full animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
                <FeatureGrid />
            </div>
        </div>
    );
};

export default Home;
