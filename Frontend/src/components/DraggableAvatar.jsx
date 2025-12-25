import React, { useState, useEffect, useRef } from 'react';
import AvatarChatbot from './AvatarChatbot';

const DraggableAvatar = () => {
    const [image, setImage] = useState(null);
    const [settings, setSettings] = useState({
        position: { x: 0, y: 0.5, z: -4 },
        rotation: { x: 0, y: 180, z: 0 },
        scale: 0.6,
        pinMode: true
    });
    const [dragPosition, setDragPosition] = useState({ x: window.innerWidth - 150, y: 100 });
    const [isDragging, setIsDragging] = useState(false);
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const [clickStart, setClickStart] = useState({ x: 0, y: 0 });

    useEffect(() => {
        // Load from localStorage
        const loadSettings = () => {
            const savedImage = localStorage.getItem('avatarImage');
            setImage(savedImage);

            setSettings({
                position: JSON.parse(localStorage.getItem('avatarPosition') || '{"x":0,"y":0.5,"z":-4}'),
                rotation: JSON.parse(localStorage.getItem('avatarRotation') || '{"x":0,"y":180,"z":0}'),
                scale: parseFloat(localStorage.getItem('avatarScale') || '0.6'),
                pinMode: JSON.parse(localStorage.getItem('avatarPinMode') || 'true')
            });

            const savedDragPos = localStorage.getItem('avatarDragPosition');
            if (savedDragPos) {
                setDragPosition(JSON.parse(savedDragPos));
            }
        };

        loadSettings();

        // Listen for storage changes from Avatar page
        window.addEventListener('storage', loadSettings);

        // Custom event for same-window updates
        const handleAvatarUpdate = () => loadSettings();
        window.addEventListener('avatarUpdate', handleAvatarUpdate);

        return () => {
            window.removeEventListener('storage', loadSettings);
            window.removeEventListener('avatarUpdate', handleAvatarUpdate);
        };
    }, []);

    const handleMouseDown = (e) => {
        if (settings.pinMode) return; // Can't drag in pin mode

        setIsDragging(true);
        setClickStart({ x: e.clientX, y: e.clientY });
        setDragStart({
            x: e.clientX - dragPosition.x,
            y: e.clientY - dragPosition.y
        });
        e.preventDefault();
    };

    const handleMouseMove = (e) => {
        if (isDragging && !settings.pinMode) {
            const newX = e.clientX - dragStart.x;
            const newY = e.clientY - dragStart.y;

            // Keep within viewport bounds
            const avatarSize = 128 * settings.scale;
            const maxX = window.innerWidth - avatarSize;
            const maxY = window.innerHeight - avatarSize;

            setDragPosition({
                x: Math.max(0, Math.min(newX, maxX)),
                y: Math.max(0, Math.min(newY, maxY))
            });
        }
    };

    const handleMouseUp = (e) => {
        if (isDragging) {
            setIsDragging(false);

            // Save drag position
            localStorage.setItem('avatarDragPosition', JSON.stringify(dragPosition));

            // Check if it was a click (< 5px movement)
            const distance = Math.sqrt(
                Math.pow(e.clientX - clickStart.x, 2) +
                Math.pow(e.clientY - clickStart.y, 2)
            );

            if (distance < 5) {
                setIsChatOpen(!isChatOpen);
            }
        }
    };

    useEffect(() => {
        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
            return () => {
                window.removeEventListener('mousemove', handleMouseMove);
                window.removeEventListener('mouseup', handleMouseUp);
            };
        }
    }, [isDragging]);

    // Don't render if no image uploaded (AFTER all hooks)
    if (!image) return null;

    // Calculate transform based on settings
    const transform = `
        translate(${dragPosition.x}px, ${dragPosition.y}px)
        rotateX(${settings.rotation.x}deg)
        rotateY(${settings.rotation.y}deg)
        rotateZ(${settings.rotation.z}deg)
        scale(${settings.scale})
    `;

    return (
        <>
            <div
                onMouseDown={handleMouseDown}
                style={{
                    position: 'fixed',
                    left: 0,
                    top: 0,
                    transform,
                    cursor: settings.pinMode ? 'default' : (isDragging ? 'grabbing' : 'grab'),
                    zIndex: 9999,
                    transformOrigin: 'center',
                    transition: isDragging ? 'none' : 'transform 0.3s ease',
                    userSelect: 'none'
                }}
                className="w-32 h-32 rounded-full shadow-2xl overflow-hidden hover:scale-110 transition-transform"
            >
                <img
                    src={image}
                    alt="Avatar"
                    className="w-full h-full object-cover pointer-events-none"
                    draggable="false"
                />
            </div>

            {isChatOpen && (
                <AvatarChatbot
                    position={dragPosition}
                    onClose={() => setIsChatOpen(false)}
                />
            )}
        </>
    );
};

export default DraggableAvatar;
