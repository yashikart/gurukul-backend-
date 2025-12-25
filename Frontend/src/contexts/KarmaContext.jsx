import React, { createContext, useContext, useState, useEffect } from 'react';

const KarmaContext = createContext();

export const useKarma = () => {
    const context = useContext(KarmaContext);
    if (!context) {
        throw new Error('useKarma must be used within KarmaProvider');
    }
    return context;
};

export const KarmaProvider = ({ children }) => {
    const [karma, setKarma] = useState(() => {
        const saved = localStorage.getItem('gurukul_karma');
        return saved ? parseInt(saved, 10) : 120;
    });

    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        localStorage.setItem('gurukul_karma', karma.toString());
    }, [karma]);

    const addKarma = (amount, reason) => {
        const newKarma = karma + amount;
        setKarma(newKarma);

        // Add notification
        const notification = {
            id: Date.now(),
            type: amount > 0 ? 'positive' : 'negative',
            amount,
            reason,
            timestamp: Date.now()
        };

        setNotifications(prev => [...prev, notification]);

        // Auto-remove notification after 3 seconds
        setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, 3000);
    };

    const removeNotification = (id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    return (
        <KarmaContext.Provider value={{ karma, addKarma, notifications, removeNotification }}>
            {children}
        </KarmaContext.Provider>
    );
};
