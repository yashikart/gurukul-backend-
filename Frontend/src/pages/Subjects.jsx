import React from 'react';
import Sidebar from '../components/Sidebar';
import { FaBook, FaLightbulb, FaBookOpen } from 'react-icons/fa';
import { useKarma } from '../contexts/KarmaContext';
import { containsProfanity } from '../utils/profanityDetector';
import API_BASE_URL from '../config';

const Subjects = () => {
    const { addKarma } = useKarma();
    const [subject, setSubject] = React.useState(() => localStorage.getItem('subjects_subject') || '');
    const [topic, setTopic] = React.useState(() => localStorage.getItem('subjects_topic') || '');
    const [loading, setLoading] = React.useState(false);
    const [result, setResult] = React.useState(() => {
        const saved = localStorage.getItem('subjects_result');
        return saved ? JSON.parse(saved) : null;
    });
    const [chatInput, setChatInput] = React.useState('');
    const [chatHistory, setChatHistory] = React.useState(() => {
        const saved = localStorage.getItem('subjects_chatHistory');
        return saved ? JSON.parse(saved) : [];
    });
    const [chatLoading, setChatLoading] = React.useState(false);
    const [hasReceivedChatKarma, setHasReceivedChatKarma] = React.useState(false);

    // Persistence Effects
    React.useEffect(() => {
        localStorage.setItem('subjects_subject', subject);
    }, [subject]);

    React.useEffect(() => {
        localStorage.setItem('subjects_topic', topic);
    }, [topic]);

    React.useEffect(() => {
        if (result) {
            localStorage.setItem('subjects_result', JSON.stringify(result));
        } else {
            localStorage.removeItem('subjects_result');
        }
    }, [result]);

    React.useEffect(() => {
        localStorage.setItem('subjects_chatHistory', JSON.stringify(chatHistory));
    }, [chatHistory]);

    const handleGenerate = async () => {
        if (!subject || !topic) {
            alert('Please enter both subject and topic');
            return;
        }

        setLoading(true);
        setResult(null);
        setChatHistory([]); // Reset chat for new topic

        try {
            const response = await fetch(`${API_BASE_URL}/subject-explorer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subject,
                    topic,
                    provider: 'groq' // Default provider
                }),
            });

            const data = await response.json();
            if (data.success) {
                setResult(data);
                setHasReceivedChatKarma(false);
                addKarma(20, 'Content generated! 📚');
                // Pre-seed chat history? No, let's keep it clean.
            } else {
                alert('Failed to generate content: ' + (data.detail || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to connect to server. Is backend running?');
        } finally {
            setLoading(false);
        }
    };

    const handleChat = async () => {
        if (!chatInput.trim() || !result) return;

        // Check for profanity
        if (containsProfanity(chatInput)) {
            addKarma(-20, 'Inappropriate language detected ⚠️');
            alert('Please keep the conversation respectful.');
            return;
        }

        const userMessage = chatInput;
        setChatInput('');
        setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);
        setChatLoading(true);

        // Award karma for first chat message
        if (!hasReceivedChatKarma) {
            addKarma(20, 'Started learning conversation! 💬');
            setHasReceivedChatKarma(true);
        }

        try {
            // Construct context-aware prompt
            const contextMessage = `Context from generated lesson on ${result.topic} (${result.subject}):\n${result.notes}\n\nUser Question: ${userMessage}`;

            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: contextMessage,
                    provider: 'groq',
                    use_rag: false // We are providing context directly
                }),
            });

            const data = await response.json();
            if (data.success) {
                setChatHistory(prev => [...prev, { role: 'assistant', content: data.response }]);
            } else {
                setChatHistory(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error responding to that.' }]);
            }
        } catch (error) {
            console.error('Chat Error:', error);
            setChatHistory(prev => [...prev, { role: 'assistant', content: 'Network error. Please try again.' }]);
        } finally {
            setChatLoading(false);
        }
    };

    // Custom Markdown Renderer
    const renderContent = (text) => {
        if (!text) return null;

        // Split by lines to process block by block
        const lines = text.split('\n');
        const elements = [];

        let currentList = [];
        let listType = null; // 'ul' or 'ol'

        const flushList = () => {
            if (currentList.length > 0) {
                const ListTag = listType === 'ul' ? 'ul' : 'ol';
                const listClass = listType === 'ul' ? 'list-disc pl-6 space-y-2 mb-6 text-gray-300' : 'list-decimal pl-6 space-y-2 mb-6 text-gray-300';

                elements.push(
                    <ListTag key={`list-${elements.length}`} className={listClass}>
                        {currentList.map((item, idx) => (
                            <li key={idx}>
                                {parseInlineStyles(item)}
                            </li>
                        ))}
                    </ListTag>
                );
                currentList = [];
                listType = null;
            }
        };

        const parseInlineStyles = (text) => {
            // Split by bold syntax (**text**)
            const parts = text.split(/(\*\*.*?\*\*)/g);
            return parts.map((part, index) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={index} className="text-white font-bold">{part.slice(2, -2)}</strong>;
                }
                return part;
            });
        };

        lines.forEach((line, index) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) {
                flushList();
                return;
            }

            // Headers
            if (trimmedLine.startsWith('## ')) {
                flushList();
                elements.push(
                    <h2 key={`h2-${index}`} className="text-2xl font-bold text-accent mt-8 mb-4 border-l-4 border-accent pl-4">
                        {trimmedLine.replace('## ', '')}
                    </h2>
                );
            }
            else if (trimmedLine.startsWith('### ')) {
                flushList();
                elements.push(
                    <h3 key={`h3-${index}`} className="text-xl font-semibold text-white mt-6 mb-3">
                        {trimmedLine.replace('### ', '')}
                    </h3>
                );
            }
            // Bullet Lists
            else if (trimmedLine.startsWith('* ') || trimmedLine.startsWith('- ')) {
                if (listType === 'ol') flushList();
                listType = 'ul';
                currentList.push(trimmedLine.substring(2));
            }
            // Numbered Lists (Simple detection for 1. 2. etc)
            else if (/^\d+\.\s/.test(trimmedLine)) {
                if (listType === 'ul') flushList();
                listType = 'ol';
                currentList.push(trimmedLine.replace(/^\d+\.\s/, ''));
            }
            // Regular Paragraphs
            else {
                flushList();
                elements.push(
                    <p key={`p-${index}`} className="text-gray-300 leading-relaxed mb-4 text-lg">
                        {parseInlineStyles(trimmedLine)}
                    </p>
                );
            }
        });

        flushList(); // Flush any remaining list items
        return elements;
    };

    // Simplified Markdown Renderer for Chat
    const renderChatContent = (text) => {
        if (!text) return null;

        const lines = text.split('\n');
        const elements = [];

        let currentList = [];
        let listType = null;

        const flushList = () => {
            if (currentList.length > 0) {
                const ListTag = listType === 'ul' ? 'ul' : 'ol';
                const listClass = listType === 'ul' ? 'list-disc pl-4 space-y-1 mb-2' : 'list-decimal pl-4 space-y-1 mb-2';

                elements.push(
                    <ListTag key={`chat-list-${elements.length}`} className={listClass}>
                        {currentList.map((item, idx) => (
                            <li key={idx}>
                                {parseInlineStyles(item)}
                            </li>
                        ))}
                    </ListTag>
                );
                currentList = [];
                listType = null;
            }
        };

        const parseInlineStyles = (text) => {
            const parts = text.split(/(\*\*.*?\*\*)/g);
            return parts.map((part, index) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={index} className="font-bold">{part.slice(2, -2)}</strong>;
                }
                return part;
            });
        };

        lines.forEach((line, index) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) {
                flushList();
                return;
            }

            if (trimmedLine.startsWith('## ') || trimmedLine.startsWith('### ')) {
                flushList();
                elements.push(
                    <strong key={`h-${index}`} className="block mt-3 mb-1 font-bold text-accent">
                        {trimmedLine.replace(/^#+ /, '')}
                    </strong>
                );
            }
            else if (trimmedLine.startsWith('* ') || trimmedLine.startsWith('- ')) {
                if (listType === 'ol') flushList();
                listType = 'ul';
                currentList.push(trimmedLine.substring(2));
            }
            else if (/^\d+\.\s/.test(trimmedLine)) {
                if (listType === 'ul') flushList();
                listType = 'ol';
                currentList.push(trimmedLine.replace(/^\d+\.\s/, ''));
            }
            else {
                flushList();
                elements.push(
                    <p key={`p-${index}`} className="mb-2 leading-relaxed">
                        {parseInlineStyles(trimmedLine)}
                    </p>
                );
            }
        });

        flushList();
        return elements;
    };

    return (
        <div className="flex pt-20 sm:pt-24 min-h-screen container mx-auto px-2 sm:px-4 gap-3 sm:gap-6 pb-8 sm:pb-12">
            {/* Left Sidebar */}
            <Sidebar />

            {/* Main Content Area */}
            <main className="flex-grow flex flex-col gap-4 sm:gap-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>

                {/* Center Panel - Subject Explorer Form */}
                {!loading && !result && (
                    <div className="flex-grow glass-panel no-hover p-4 sm:p-6 md:p-10 rounded-3xl border border-white/10 relative overflow-hidden flex flex-col items-center justify-center text-center shadow-2xl">

                        {/* Header */}
                        <div className="mb-6 sm:mb-8">
                            <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold font-heading text-transparent bg-clip-text bg-gradient-to-r from-orange-100 to-orange-50 mb-3 sm:mb-4 drop-shadow-sm">
                                Subject Explorer
                            </h1>
                            <p className="text-gray-300 max-w-lg mx-auto font-light text-sm sm:text-base px-4">
                                Select a subject and enter a topic to begin your learning journey
                            </p>
                        </div>

                        {/* Form Container */}
                        <div className="w-full max-w-xl bg-black/60 backdrop-blur-sm p-4 sm:p-6 rounded-2xl border border-white/5 shadow-inner">

                            {/* Subject Input */}
                            <div className="mb-3 sm:mb-4 text-left">
                                <label className="block text-gray-300 text-xs sm:text-sm font-semibold mb-2 ml-1">Subject:</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                        <FaBook className="text-gray-500 group-focus-within:text-accent transition-colors" />
                                    </div>
                                    <input
                                        type="text"
                                        value={subject}
                                        onChange={(e) => setSubject(e.target.value)}
                                        placeholder="Type any subject (e.g. Mathematics)"
                                        className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50 transition-all font-medium"
                                    />
                                </div>
                            </div>

                            {/* Topic Input */}
                            <div className="mb-4 sm:mb-6 text-left">
                                <label className="block text-gray-300 text-xs sm:text-sm font-semibold mb-2 ml-1">Topic:</label>
                                <div className="relative group">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                        <FaLightbulb className="text-gray-500 group-focus-within:text-accent transition-colors" />
                                    </div>
                                    <input
                                        type="text"
                                        value={topic}
                                        onChange={(e) => setTopic(e.target.value)}
                                        placeholder="Enter a topic needed"
                                        className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent/50 transition-all font-medium"
                                    />
                                </div>
                            </div>

                            {/* Action Button */}
                            <button
                                onClick={handleGenerate}
                                className="w-full py-3 sm:py-4 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-white font-bold text-base sm:text-lg rounded-xl shadow-lg transition-all transform hover:-translate-y-1 flex items-center justify-center gap-2"
                            >
                                <FaBookOpen />
                                Generate Lesson
                            </button>
                        </div>
                    </div>
                )}

                {/* Loading State */}
                {loading && (
                    <div className="flex-grow flex flex-col items-center justify-center p-6 sm:p-10">
                        <div className="animate-spin h-12 w-12 sm:h-16 sm:w-16 border-4 border-accent border-t-transparent rounded-full mb-4 sm:mb-6 shadow-lg shadow-accent/20"></div>
                        <h2 className="text-xl sm:text-2xl font-bold text-white mb-2 animate-pulse text-center px-4">Generating your lesson...</h2>
                        <p className="text-gray-400 text-sm sm:text-base text-center px-4">Consulting AI Knowledge Base • Curating Videos • Structuring Notes</p>
                    </div>
                )}

                {/* RESULTS SECTION */}
                {result && (
                    <div className="animate-fade-in-up">

                        {/* Notes & Chat Container */}
                        <div className="glass-panel p-3 sm:p-4 md:p-8 rounded-3xl border border-white/10 mb-4 sm:mb-6 bg-black/40">
                            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-0 mb-6 sm:mb-8 border-b border-white/10 pb-4 sm:pb-6">
                                <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-300 to-amber-200 flex items-center gap-2 sm:gap-3">
                                    <FaBookOpen className="text-orange-400 text-lg sm:text-xl" />
                                    {result.topic}
                                </h2>
                                <button
                                    onClick={() => setResult(null)}
                                    className="px-4 py-2 bg-white/5 hover:bg-white/10 text-sm text-gray-400 hover:text-white rounded-lg transition-colors border border-white/5 flex items-center gap-2"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                                    Explore New Topic
                                </button>
                            </div>

                            {/* Notes Content */}
                            <div className="prose prose-invert max-w-none text-gray-200 leading-relaxed mb-6 sm:mb-8 p-4 sm:p-6 md:p-8 bg-black/20 rounded-2xl border border-white/5 shadow-inner text-sm sm:text-base">
                                {renderContent(result.notes)}
                            </div>

                            {/* Divider */}
                            <div className="h-px bg-white/10 my-8"></div>

                            {/* Contextual Chat Interface */}
                            <div className="bg-black/40 rounded-xl p-4 sm:p-6 border border-white/5">
                                <h3 className="text-base sm:text-lg font-semibold text-white mb-3 sm:mb-4 flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                    Ask doubts about this topic
                                </h3>

                                {/* Chat History */}
                                {chatHistory.length > 0 && (
                                    <div className="mb-3 sm:mb-4 max-h-48 sm:max-h-60 overflow-y-auto space-y-2 sm:space-y-3 custom-scrollbar pr-2">
                                        {chatHistory.map((msg, idx) => (
                                            <div key={idx} className={`p-4 rounded-xl text-base ${msg.role === 'user' ? 'bg-orange-900/30 ml-auto border border-orange-500/20 max-w-[80%]' : 'bg-white/5 border border-white/10 max-w-[90%]'}`}>
                                                <span className={`font-bold block text-xs mb-1 ${msg.role === 'user' ? 'text-orange-400' : 'text-purple-400'}`}>
                                                    {msg.role === 'user' ? 'You' : 'AI Tutor'}
                                                </span>
                                                {renderChatContent(msg.content)}
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Chat Input */}
                                <div className="relative flex gap-2">
                                    <input
                                        type="text"
                                        value={chatInput}
                                        onChange={(e) => setChatInput(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                                        placeholder="Ask a follow-up question..."
                                        className="flex-grow px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent/50"
                                    />
                                    <button
                                        onClick={handleChat}
                                        disabled={chatLoading}
                                        className="px-4 sm:px-6 py-2 sm:py-3 text-sm sm:text-base bg-accent text-black font-bold rounded-xl hover:bg-accent/90 transition-colors disabled:opacity-50"
                                    >
                                        {chatLoading ? '...' : 'Send'}
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* YouTube Recommendations */}
                        <div className="glass-panel p-4 sm:p-6 md:p-8 rounded-3xl border border-white/10 bg-black/40">
                            <h2 className="text-xl sm:text-2xl font-bold text-red-500 mb-4 sm:mb-6 flex items-center gap-2 sm:gap-3">
                                {/* Using text for icon if FaYoutube not imported, but assuming it works or fallback */}
                                Video Recommendations
                            </h2>

                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                                {result.youtube_recommendations.map((video, idx) => (
                                    <a
                                        key={idx}
                                        href={video.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block group bg-black/60 rounded-xl overflow-hidden border border-white/5 hover:border-red-500/50 transition-all hover:transform hover:-translate-y-1"
                                    >
                                        <div className="relative aspect-video">
                                            <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover" />
                                            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center">
                                                    <div className="w-0 h-0 border-t-8 border-t-transparent border-l-12 border-l-white border-b-8 border-b-transparent ml-1"></div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="p-4">
                                            <h3 className="text-white font-medium line-clamp-2 mb-2 group-hover:text-red-400 transition-colors">{video.title}</h3>
                                            <p className="text-gray-400 text-sm">{video.channel_title}</p>
                                        </div>
                                    </a>
                                ))}
                            </div>
                        </div>

                    </div>
                )}

            </main>
        </div>
    );
};

export default Subjects;
