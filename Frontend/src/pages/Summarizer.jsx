import React from 'react';
import Sidebar from '../components/Sidebar';
import { FaFileUpload, FaCloudUploadAlt, FaMagic, FaChevronDown } from 'react-icons/fa';
import { useKarma } from '../contexts/KarmaContext';
import API_BASE_URL from '../config';

const Summarizer = () => {
    const { addKarma } = useKarma();
    const [selectedModel, setSelectedModel] = React.useState(() => localStorage.getItem('summarizer_selectedModel') || 'Uniguru');
    const [summaryType, setSummaryType] = React.useState(() => localStorage.getItem('summarizer_summaryType') || 'concise');
    const [isSummaryTypeOpen, setIsSummaryTypeOpen] = React.useState(false);
    const [file, setFile] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [result, setResult] = React.useState(() => {
        const saved = localStorage.getItem('summarizer_result');
        return saved ? JSON.parse(saved) : null;
    });
    const [progress, setProgress] = React.useState(0);
    const [error, setError] = React.useState(null);
    const [chatInput, setChatInput] = React.useState('');
    const [chatHistory, setChatHistory] = React.useState(() => {
        const saved = localStorage.getItem('summarizer_chatHistory');
        return saved ? JSON.parse(saved) : [];
    });
    const [chatLoading, setChatLoading] = React.useState(false);

    // Persistence Effects
    React.useEffect(() => {
        localStorage.setItem('summarizer_selectedModel', selectedModel);
    }, [selectedModel]);

    React.useEffect(() => {
        localStorage.setItem('summarizer_summaryType', summaryType);
    }, [summaryType]);

    React.useEffect(() => {
        if (result) {
            localStorage.setItem('summarizer_result', JSON.stringify(result));
        } else {
            localStorage.removeItem('summarizer_result');
        }
    }, [result]);

    React.useEffect(() => {
        localStorage.setItem('summarizer_chatHistory', JSON.stringify(chatHistory));
    }, [chatHistory]);

    const handleNewUpload = () => {
        if (window.confirm("This will clear your current analysis. Continue?")) {
            setFile(null);
            setResult(null);
            setChatHistory([]);
            setError(null);
            setProgress(0);
            localStorage.removeItem('summarizer_result');
            localStorage.removeItem('summarizer_chatHistory');
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setResult(null);
            setError(null);
            setProgress(0);
        }
    };

    const handleSummarize = async () => {
        if (!file) {
            setError("Please upload a file first.");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);
        setProgress(0);

        // Simulate progress based on file size and summary type
        // Base time: 20s (Very conservative to ensure it doesn't rush)
        // + Time per MB of file size (approx 10s per MB processing)
        const fileSizeMB = file.size / (1024 * 1024);
        let baseTime = 20000 + (fileSizeMB * 10000);

        let multiplier = 1;
        if (summaryType === 'detailed') multiplier = 1.5;
        if (summaryType === 'comprehensive') multiplier = 3;

        // Clamp minimum time to 20s, max to 120s
        const duration = Math.min(Math.max(baseTime * multiplier, 20000), 120000);

        const interval = 100;
        // Target 85% by 'duration'. This leaves a distinct 15% chunk for the actual completion event.
        // If the server finishes early, it jumps a bit. If it takes longer, it crawls in the 85-90% range.
        // Curve: progress = 90 * (1 - e^(-t / timeConstant))
        const timeConstant = duration / 2; // Slower curve

        let elapsed = 0;
        const progressTimer = setInterval(() => {
            elapsed += interval;
            setProgress(prev => {
                if (prev >= 90) return prev; // Cap at 90% strictly until response
                // Asymptotic approach
                const calculated = 90 * (1 - Math.exp(-elapsed / timeConstant));
                return Math.max(prev, calculated); // Monotonic increase
            });
        }, interval);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('summary_type', summaryType);

        // Determine endpoint based on file type
        let endpoint = `${API_BASE_URL}/summarize-doc`;
        if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
            endpoint = `${API_BASE_URL}/summarize-pdf`;
        }

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate summary');
            }

            // Complete progress
            clearInterval(progressTimer);
            setProgress(100);

            const data = await response.json();

            // Small delay to let user see 100%
            setTimeout(() => {
                setResult(data);
                addKarma(20, 'Document summarized! 📄');
                setLoading(false);
                setProgress(0);
            }, 500);

        } catch (err) {
            clearInterval(progressTimer);
            setProgress(0);
            console.error("Summarization error:", err);
            setError(err.message || "An unexpected error occurred.");
            setLoading(false);
        }
    };

    // Chat Logic
    const handleChat = async () => {
        if (!chatInput.trim()) return;

        const userMessage = { role: 'user', content: chatInput };
        setChatHistory(prev => [...prev, userMessage]);
        setChatInput('');
        setChatLoading(true);

        try {
            // Context preparation for the first message or if context is missing
            let prompt = chatInput;

            // If it's the start of the conversation, inject the context
            // We check if history is empty OR if we want to ensure context is always available.
            // A simple strategy is to prepend context if history is empty.
            if (chatHistory.length === 0 && result) {
                const summaryText = result.overall_summary || result.summary || '';
                prompt = `Context: The user has uploaded a document named "${file?.name || 'Document'}". contents summary:\n${summaryText}\n\nUser Question: ${chatInput}`;
            }

            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: prompt,
                    conversation_id: `summ-${Date.now()}`, // Simple session-based ID
                    provider: 'auto' // Use auto provider
                })
            });

            if (!response.ok) throw new Error('Failed to get response');

            const data = await response.json();
            const botMessage = { role: 'assistant', content: data.response };
            setChatHistory(prev => [...prev, botMessage]);

        } catch (error) {
            console.error("Chat error:", error);
            const errorMessage = { role: 'assistant', content: "I'm sorry, I couldn't process your request. Please try again." };
            setChatHistory(prev => [...prev, errorMessage]);
        } finally {
            setChatLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleChat();
        }
    };

    // simplified chat markdown
    const renderChatContent = (text) => {
        return text.split('\n').map((line, i) => {
            if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
                return <li key={i} className="ml-4 list-disc">{line.trim().substring(2)}</li>;
            }
            // Bold
            const parts = line.split(/(\*\*.*?\*\*)/g);
            return (
                <p key={i} className="mb-1">
                    {parts.map((part, j) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={j} className="text-accent font-bold">{part.slice(2, -2)}</strong>;
                        }
                        return part;
                    })}
                </p>
            );
        });
    };

    // Simplified Markdown Renderer for Summary
    const renderSummaryContent = (text) => {
        if (!text) return null;

        return text.split('\n').map((line, index) => {
            const trimmedLine = line.trim();
            if (!trimmedLine) return <br key={index} />;

            // Helper for inline bolding
            const parseInlineStyles = (str) => {
                const parts = str.split(/(\*\*.*?\*\*)/g);
                return parts.map((part, i) => {
                    if (part.startsWith('**') && part.endsWith('**')) {
                        return <strong key={i} className="text-accent font-bold">{part.slice(2, -2)}</strong>;
                    }
                    return part;
                });
            };

            // Headers
            if (trimmedLine.startsWith('## ')) {
                return (
                    <h2 key={index} className="text-3xl font-bold text-accent mt-8 mb-4 border-l-4 border-accent pl-4">
                        {trimmedLine.replace('## ', '')}
                    </h2>
                );
            }
            if (trimmedLine.startsWith('### ')) {
                return (
                    <h3 key={index} className="text-2xl font-semibold text-white mt-6 mb-3">
                        {trimmedLine.replace('### ', '')}
                    </h3>
                );
            }

            // Lists
            if (trimmedLine.startsWith('* ') || trimmedLine.startsWith('- ') || trimmedLine.startsWith('• ')) {
                return (
                    <div key={index} className="flex gap-3 mb-2 ml-4">
                        <span className="text-accent mt-1.5">•</span>
                        <p className="text-gray-200 text-lg leading-relaxed flex-1">
                            {parseInlineStyles(trimmedLine.replace(/^[*•-]\s/, ''))}
                        </p>
                    </div>
                );
            }

            // Paragraphs
            return (
                <p key={index} className="text-gray-200 text-lg leading-loose mb-4">
                    {parseInlineStyles(trimmedLine)}
                </p>
            );
        });
    };

    // Helper to format large numbers
    const formatNumber = (num) => {
        return num ? num.toLocaleString() : '0';
    };

    return (
        <div className="flex pt-24 min-h-screen container mx-auto px-4 gap-6 pb-12">
            {/* Left Sidebar */}
            <Sidebar />

            {/* Main Content Area */}
            <main className="flex-grow flex flex-col gap-6 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>

                {/* Center Panel - Smart Document Analysis */}
                {!result && (
                    <div className="flex-grow glass-panel no-hover p-10 rounded-3xl border border-white/10 relative overflow-hidden flex flex-col items-center justify-center text-center shadow-2xl min-h-[500px]">

                        {/* Header */}
                        <div className="mb-8">
                            <h1 className="text-5xl font-bold font-heading text-white mb-4 drop-shadow-sm">
                                Smart Document Analysis
                            </h1>
                            <p className="text-lg text-gray-300 max-w-xl mx-auto font-light">
                                Upload your documents for instant AI-powered summaries
                            </p>
                            <p className="text-xs text-gray-500 mt-2">
                                Supported formats: PDF, DOCX • Max size: 10MB
                            </p>
                        </div>

                        {/* Controls Container */}
                        <div className="flex flex-wrap items-center justify-center gap-6 mb-8 w-full max-w-2xl">

                            {/* AI Model Selector */}
                            <div className="flex flex-col items-start gap-2">
                                <label className="text-xs font-semibold text-accent/80 uppercase tracking-wider ml-1">AI Model</label>
                                <div className="relative">
                                    <div className="bg-white/10 border border-white/10 text-white py-3 px-6 rounded-xl text-center font-medium cursor-default min-w-[140px]">
                                        Uniguru
                                    </div>
                                </div>
                            </div>

                            {/* Summary Type Selector (Custom Dropdown) */}
                            <div className="flex flex-col items-start gap-2">
                                <label className="text-xs font-semibold text-accent/80 uppercase tracking-wider ml-1">Summary Type</label>
                                <div className="relative">
                                    <button
                                        onClick={() => setIsSummaryTypeOpen(!isSummaryTypeOpen)}
                                        onBlur={() => setTimeout(() => setIsSummaryTypeOpen(false), 200)}
                                        className={`flex items-center justify-between gap-3 bg-white/10 border text-white py-3 px-6 rounded-xl transition-all duration-300 font-medium min-w-[160px] ${isSummaryTypeOpen ? 'border-accent/50 ring-2 ring-accent/20 bg-white/20' : 'border-white/10 hover:bg-white/20'}`}
                                    >
                                        <span className="capitalize">{summaryType}</span>
                                        <FaChevronDown className={`text-xs text-gray-400 transition-transform duration-300 ${isSummaryTypeOpen ? 'rotate-180' : ''}`} />
                                    </button>

                                    <div className={`absolute top-full mt-2 left-0 w-full bg-[#1a1c16]/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden transition-all duration-300 z-50 ${isSummaryTypeOpen ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-2 pointer-events-none'}`}>
                                        {['concise', 'detailed', 'comprehensive'].map((type) => (
                                            <div
                                                key={type}
                                                onClick={() => {
                                                    setSummaryType(type);
                                                    setIsSummaryTypeOpen(false);
                                                }}
                                                className="px-4 py-3 text-sm text-gray-300 hover:bg-white/10 hover:text-accent cursor-pointer transition-colors flex items-center justify-between group capitalize"
                                            >
                                                {type}
                                                {summaryType === type && <div className="w-1.5 h-1.5 rounded-full bg-accent shadow-[0_0_5px_rgba(232,185,117,0.8)]"></div>}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Drop Zone / File Display */}
                        <div className="w-full max-w-lg mb-8">
                            <label
                                htmlFor="file-upload"
                                className={`flex flex-col items-center justify-center w-full h-56 border-2 border-dashed rounded-3xl cursor-pointer transition-all duration-300 group ${file ? 'border-accent/50 bg-accent/5' : 'border-white/20 bg-white/5 hover:bg-white/10'}`}
                            >
                                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                    {file ? (
                                        <>
                                            <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center mb-3">
                                                <FaFileUpload className="w-8 h-8 text-accent" />
                                            </div>
                                            <p className="mb-1 text-lg text-white font-medium truncate max-w-[90%]">
                                                {file.name}
                                            </p>
                                            <p className="text-sm text-gray-400">
                                                {(file.size / 1024 / 1024).toFixed(2)} MB
                                            </p>
                                            <span className="mt-3 text-xs text-accent hover:underline">Click to change file</span>
                                        </>
                                    ) : (
                                        <>
                                            <FaCloudUploadAlt className="w-16 h-16 text-gray-400 mb-4 group-hover:text-accent transition-colors group-hover:scale-110 transform duration-300" />
                                            <p className="mb-2 text-lg text-gray-300 font-medium">
                                                Drop your file here
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                or click to browse
                                            </p>
                                        </>
                                    )}
                                </div>
                                <input id="file-upload" type="file" className="hidden" onChange={handleFileChange} accept=".pdf,.doc,.docx" />
                            </label>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-200 text-sm flex items-center gap-2 animate-pulse">
                                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                {error}
                            </div>
                        )}

                        {/* Action Button */}
                        <div className="w-full max-w-sm">
                            <button
                                onClick={handleSummarize}
                                disabled={loading || !file}
                                className={`relative w-full py-4 font-bold text-lg rounded-xl shadow-lg border border-white/10 transition-all transform flex items-center justify-center gap-3 overflow-hidden ${loading || !file ? 'bg-gray-700/50 text-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-gray-700 to-gray-600 hover:from-gray-600 hover:to-gray-500 text-white hover:-translate-y-1 hover:border-white/20'}`}
                            >
                                {/* Progress Bar Background */}
                                {loading && (
                                    <div
                                        className="absolute left-0 top-0 h-full bg-accent/20 transition-all duration-100 ease-out"
                                        style={{ width: `${progress}%` }}
                                    ></div>
                                )}

                                {/* Button Content (z-index to stay on top) */}
                                <div className="relative z-10 flex items-center gap-3">
                                    {loading ? (
                                        <>
                                            <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                                            Analyzing Document ({Math.round(progress)}%)...
                                        </>
                                    ) : (
                                        <>
                                            <FaMagic className={!file ? 'text-gray-500' : 'text-accent'} />
                                            Generate Summary
                                        </>
                                    )}
                                </div>
                            </button>
                        </div>
                    </div>
                )}

                {/* Result Section with Chat */}
                {result && (
                    <div className="flex flex-col lg:flex-row gap-6 animate-fade-in-up h-auto lg:h-[calc(100vh-140px)]">
                        {/* Summary Column (Left - Scrollable) */}
                        <div className="lg:w-3/5 glass-panel p-8 rounded-3xl border border-white/10 bg-black/40 flex flex-col h-full overflow-hidden">
                            <div className="flex justify-between items-center mb-6 border-b border-white/10 pb-4 shrink-0">
                                <div className="flex items-center gap-4">
                                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                                        <FaMagic className="text-accent" />
                                        Analysis Result
                                    </h2>
                                    <button
                                        onClick={handleNewUpload}
                                        className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-medium transition-colors border border-white/10"
                                    >
                                        Upload New Document
                                    </button>
                                </div>
                                <div className="flex gap-4 text-xs text-gray-400">
                                    {/* Stats here if needed, keeping it minimal for space */}
                                    <span className="text-accent font-medium">{formatNumber((result.overall_summary || result.summary || '').length)} Chars</span>
                                </div>
                            </div>

                            <div className="overflow-y-auto pr-2 custom-scrollbar">
                                <div className="prose prose-invert max-w-none text-gray-200 leading-relaxed bg-black/20 p-6 rounded-xl border border-white/5 shadow-inner">
                                    {renderSummaryContent(result.overall_summary || result.summary)}
                                </div>
                            </div>
                        </div>

                        {/* Chat Column (Right) */}
                        <div className="lg:w-2/5 glass-panel p-6 rounded-3xl border border-white/10 bg-black/40 flex flex-col h-full">
                            <div className="mb-4 border-b border-white/10 pb-2 shrink-0">
                                <h3 className="text-xl font-bold text-white">Chat with Document</h3>
                                <p className="text-xs text-gray-400">Ask questions about the summary</p>
                            </div>

                            {/* Chat History */}
                            <div className="flex-grow overflow-y-auto pr-2 mb-4 space-y-4 custom-scrollbar">
                                {chatHistory.length === 0 ? (
                                    <div className="h-full flex flex-col items-center justify-center text-gray-500 text-sm">
                                        <p>No messages yet.</p>
                                        <p>Ask something about the document!</p>
                                    </div>
                                ) : (
                                    chatHistory.map((msg, idx) => (
                                        <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`max-w-[85%] p-3 rounded-2xl ${msg.role === 'user' ? 'bg-accent text-black font-medium rounded-tr-none' : 'bg-white/10 text-gray-200 rounded-tl-none'}`}>
                                                {msg.role === 'user' ? msg.content : renderChatContent(msg.content)}
                                            </div>
                                        </div>
                                    ))
                                )}
                                {chatLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-white/10 p-3 rounded-2xl rounded-tl-none flex gap-2 items-center">
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Input Area */}
                            <div className="shrink-0 relative">
                                <input
                                    type="text"
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Type your question..."
                                    className="w-full bg-black/40 border border-white/10 text-white rounded-xl py-3 px-4 pr-12 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/50 placeholder-gray-600"
                                />
                                <button
                                    onClick={handleChat}
                                    disabled={chatLoading || !chatInput.trim()}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-accent text-black rounded-lg hover:bg-accent/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                                </button>
                            </div>
                        </div>
                    </div>
                )}

            </main>
        </div>
    );
};

export default Summarizer;
