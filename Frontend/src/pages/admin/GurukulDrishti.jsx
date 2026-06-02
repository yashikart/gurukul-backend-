import React, { useState } from 'react';
import { 
    FaDatabase, FaEye, FaUsers, FaGraduationCap, FaMapMarkedAlt, 
    FaUserTie, FaChevronRight, FaPlay, FaHeartbeat, FaExclamationTriangle, 
    FaChartLine, FaCheckCircle, FaLock, FaSync, FaShieldAlt, FaTerminal 
} from 'react-icons/fa';

const GurukulDrishti = () => {
    const [selectedRole, setSelectedRole] = useState("Minister");
    const [terminalLogs, setTerminalLogs] = useState([
        "System Initialized. Drishti Foundation Active.",
        "Awaiting Operator Action..."
    ]);

    const logAction = (msg) => {
        const timestamp = new Date().toLocaleTimeString();
        setTerminalLogs(prev => [`[${timestamp}] ${msg}`, ...prev.slice(0, 10)]);
    };

    // 8 TANTRA Roles Metadata
    const ROLES_METADATA = {
        "Minister": {
            title: "Union Minister of Education",
            signals: "National-scale throughput, overall system error rate, states compliance rate.",
            visibility: "Aggregate country-wide stats, all 28 states, 100% data access bounds.",
            actions: "Structural policy reforms, emergency cabinet escalations, national broadcast schedule."
        },
        "PS / OSD / Senior Admin": {
            title: "Private Secretary / OSD to Minister",
            signals: "State-level variance indicators, infrastructure latency bounds, active alerts feed.",
            visibility: "Complete audit logs, central databases schemas, state metrics.",
            actions: "Deploy convergence hotfixes, trigger schema migrations, authorize super admin status."
        },
        "District / Collector": {
            title: "District Collector / Magistrate",
            signals: "District educational health, active schools list, teacher attendance coefficient.",
            visibility: "All schools within district partition boundary, teacher telemetry.",
            actions: "Approve district remedial budgets, override local school calendars."
        },
        "School Admin / Principal": {
            title: "School Principal",
            signals: "School-wide student counts, classroom pacing distributions, SQL lock indicators.",
            visibility: "Cohorts assigned to school, individual class records.",
            actions: "Reset local Watchdog thresholds, trigger EMS sync updates, register new cohorts."
        },
        "Teacher": {
            title: "Classroom Teacher",
            signals: "Student comprehension pacing coefficients, speech hesitation rates, study time goals.",
            visibility: "Assigned cohorts, progress ledgers, student reflections feed.",
            actions: "Adjust pacing bias coefficient, issue custom flashcard sets, approve learning track milestones."
        },
        "Parent": {
            title: "Guardian",
            signals: "Child study time consistency, focus coefficient, karma balance.",
            visibility: "Child-specific study logs and progress traces only.",
            actions: "Authorize profile preferences, approve custom content suggestions."
        },
        "Student": {
            title: "Learner",
            signals: "Daily goals remaining, active learning tracks, flashcard review pacing.",
            visibility: "Personal progress, summaries, flashcards, chat history.",
            actions: "Calibrate voice STT assistant, submit reflection notes, complete conceptual quizzes."
        },
        "System Super Admin": {
            title: "System Super Administrator",
            signals: "CPU/Memory usage, SQLite write lock counts, Prometheus metrics feed.",
            visibility: "Total un-proxied platform, ChromaDB vector stores, full relational schemas.",
            actions: "Roll back schema contract versions, simulate failure states, clear databases."
        }
    };

    // Dashboard Primitives implementation
    const KPICard = ({ title, value, subText, color }) => (
        <div className="glass-panel p-5 rounded-2xl border border-white/5 bg-black/40 hover:border-orange-500/20 hover:scale-[1.02] transition-all group relative overflow-hidden">
            <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-2">{title}</div>
            <div className="text-3xl font-bold text-white mb-1 tabular-nums">{value}</div>
            <div className={`text-xs ${color} font-medium`}>{subText}</div>
            <div className="absolute -bottom-8 -right-8 w-20 h-20 bg-orange-500/5 rounded-full blur-2xl group-hover:bg-orange-500/10 transition-all"></div>
        </div>
    );

    const AlertCard = ({ title, desc, severity }) => (
        <div className={`p-4 rounded-xl border flex gap-3 ${
            severity === 'HIGH' 
                ? 'bg-red-500/10 border-red-500/20 text-red-300' 
                : 'bg-amber-500/10 border-amber-500/20 text-amber-300'
        }`}>
            <FaExclamationTriangle className="text-lg shrink-0 mt-0.5" />
            <div>
                <div className="text-xs font-bold uppercase tracking-wider">{title}</div>
                <div className="text-[10px] text-gray-400 mt-0.5">{desc}</div>
            </div>
        </div>
    );

    const ExecutiveMetricCard = ({ title, value, progress, color }) => (
        <div className="glass-panel p-5 rounded-2xl border border-white/5 bg-black/40">
            <div className="text-xs text-gray-400 mb-1">{title}</div>
            <div className="text-xl font-bold text-white mb-3">{value}</div>
            <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                <div className={`h-full ${color}`} style={{ width: `${progress}%` }}></div>
            </div>
        </div>
    );

    return (
        <div className="space-y-6 pb-12">
            {/* Header */}
            <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <FaEye className="text-orange-500" />
                    Gurukul Drishti Control Panel
                </h3>
                <p className="text-gray-400 text-xs sm:text-sm">
                    Canonical educational operating system foundation modeling signals, visibilities, and low-scope action interfaces.
                </p>
            </div>

            {/* B2. DASHBOARD CAPABILITY PRIMITIVES (CSS GRID) */}
            <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-orange-400 mb-4 flex items-center gap-2">
                    <FaCheckCircle className="text-xs" />
                    Drishti Reusable Dashboard Primitives
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <KPICard 
                        title="Active Multi-Tenant Learners" 
                        value="1,420,000" 
                        subText="➔ +4.8% growth weekly" 
                        color="text-green-400" 
                    />
                    <KPICard 
                        title="Comprehension Pacing Coefficient" 
                        value="1.08x" 
                        subText="➔ System Average" 
                        color="text-blue-400" 
                    />
                    <KPICard 
                        title="Storage Layer Sync Rate" 
                        value="99.99%" 
                        subText="➔ 0 write locks active" 
                        color="text-purple-400" 
                    />
                    <KPICard 
                        title="TANTRA Contract Compliance" 
                        value="100.0%" 
                        subText="➔ 58.2M events verified" 
                        color="text-emerald-400" 
                    />
                </div>
            </div>

            {/* Alert & Executive Metrics Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Executive Metric primitive */}
                <div className="lg:col-span-1 space-y-4">
                    <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-black/30 h-full flex flex-col justify-between">
                        <div className="space-y-4">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300">Executive Resource Analytics</h4>
                            <ExecutiveMetricCard 
                                title="Systemic CPU Optimization" 
                                value="38.5% capacity" 
                                progress={38.5} 
                                color="bg-green-500" 
                            />
                            <ExecutiveMetricCard 
                                title="Platform Memory Usage" 
                                value="118.4 MB / 512 MB" 
                                progress={23.1} 
                                color="bg-blue-500" 
                            />
                            <ExecutiveMetricCard 
                                title="SQLite Thread Pool Health" 
                                value="92.1% operational efficiency" 
                                progress={92.1} 
                                color="bg-purple-500" 
                            />
                        </div>
                    </div>
                </div>

                {/* Alerts primitive */}
                <div className="lg:col-span-1">
                    <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-black/30 h-full">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300 mb-4">Active Anomaly Signal Feed</h4>
                        <div className="space-y-3">
                            <AlertCard 
                                title="ChromaDB CBSE Bleed Prevention Triggered" 
                                desc="Dynamic metadata isolated to NCERT; cross-board NCERT leaks actively prevented." 
                                severity="LOW" 
                            />
                            <AlertCard 
                                title="Guest Syllabus Fallback Detected" 
                                desc="Unresolved tenant session redirected to NCERT English Standard 10 automatically." 
                                severity="LOW" 
                            />
                            <AlertCard 
                                title="Sovereign Voice local CPU timeout" 
                                desc="Speech interface safely fell back to public gTTS engine without thread blocks." 
                                severity="HIGH" 
                            />
                        </div>
                    </div>
                </div>

                {/* Operator Actions Card Primitive */}
                <div className="lg:col-span-1">
                    <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-black/30 h-full flex flex-col justify-between">
                        <div>
                            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-300 mb-4">Urgent Governance Actions</h4>
                            <p className="text-[10px] text-gray-400 mb-4">Direct system control loops accessible by union administrators under strict TANTRA token access keys:</p>
                        </div>
                        <div className="space-y-2">
                            <button 
                                onClick={() => logAction("Policy Reforms Drafted. Broadcast scheduled.")}
                                className="w-full py-2.5 px-4 rounded-xl bg-orange-600/10 border border-orange-500/20 text-orange-400 hover:bg-orange-500/20 hover:text-white font-bold text-xs transition-all flex items-center justify-between"
                            >
                                <span>Draft structural reforms policy</span>
                                <FaChevronRight />
                            </button>
                            <button 
                                onClick={() => logAction("Emergency cabinet escalation sequence triggered.")}
                                className="w-full py-2.5 px-4 rounded-xl bg-red-600/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 hover:text-white font-bold text-xs transition-all flex items-center justify-between"
                            >
                                <span>Emergency Escalation to Cabinet</span>
                                <FaChevronRight />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* B3. CONTROL PANEL MVP PROTOTYPES (Action-Oriented) */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Low-scope MVP Prototypes Column */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-black/30">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-orange-400 mb-4 flex items-center gap-2">
                            <FaTerminal className="text-xs" />
                            Action-Oriented MVP Dashboard Prototypes
                        </h4>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            
                            {/* Student Panel */}
                            <div className="p-4 rounded-xl border border-white/5 bg-white/5 space-y-3 flex flex-col justify-between">
                                <div>
                                    <div className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Student Panel</div>
                                    <p className="text-[10px] text-gray-500 mt-1">Actions available to learners:</p>
                                </div>
                                <div className="space-y-2 mt-3">
                                    <button 
                                        onClick={() => logAction("Student reported syllabus context fallback: redirected successfully.")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-blue-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Report Fallback Context
                                    </button>
                                    <button 
                                        onClick={() => logAction("STT Voice calibration sequence started. Audio logger listening.")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-blue-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Calibrate Voice Assistant
                                    </button>
                                    <button 
                                        onClick={() => logAction("Conceptual progress reflection note submitted to SQL database.")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-blue-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Submit Reflection Note
                                    </button>
                                </div>
                            </div>

                            {/* Teacher Panel */}
                            <div className="p-4 rounded-xl border border-white/5 bg-white/5 space-y-3 flex flex-col justify-between">
                                <div>
                                    <div className="text-[10px] font-bold text-purple-400 uppercase tracking-widest">Teacher Panel</div>
                                    <p className="text-[10px] text-gray-500 mt-1">Actions available to educators:</p>
                                </div>
                                <div className="space-y-2 mt-3">
                                    <button 
                                        onClick={() => logAction("Teacher increased classroom pacing bias by +0.10. Telemetry updated.")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-purple-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Increase Pacing Bias (+0.1)
                                    </button>
                                    <button 
                                        onClick={() => logAction("Custom flashcard set compiled & pushed to Standard 10 Marathi Medium.")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-purple-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Inject Custom Flashcards
                                    </button>
                                    <button 
                                        onClick={() => logAction("Milestone learning track approved for student stud-9921.")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-purple-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Approve Learning Milestones
                                    </button>
                                </div>
                            </div>

                            {/* School Panel */}
                            <div className="p-4 rounded-xl border border-white/5 bg-white/5 space-y-3 flex flex-col justify-between">
                                <div>
                                    <div className="text-[10px] font-bold text-orange-400 uppercase tracking-widest">School Control Panel</div>
                                    <p className="text-[10px] text-gray-500 mt-1">Actions available to principals:</p>
                                </div>
                                <div className="space-y-2 mt-3">
                                    <button 
                                        onClick={() => logAction("Watchdog thresholds reset to nominal. Escalation log cleared.")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-orange-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Reset Watchdog Thresholds
                                    </button>
                                    <button 
                                        onClick={() => logAction("Forced dynamic SQLite relational database to EMS cluster sync.")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-orange-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Force SQLite-EMS Database Sync
                                    </button>
                                    <button 
                                        onClick={() => logAction("Replay determinism hash validation run: verified match [883cca4].")}
                                        className="w-full py-2 px-3 rounded-lg bg-white/5 border border-white/5 hover:border-orange-500 text-[10px] font-bold text-gray-300 hover:text-white transition-colors text-left"
                                    >
                                        Verify Replay Hash Match
                                    </button>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>

                {/* Logs Terminal Column */}
                <div className="lg:col-span-1">
                    <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-[#080905] h-full flex flex-col justify-between">
                        <div>
                            <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-2">
                                <span className="text-xs font-bold text-green-400 font-mono flex items-center gap-2">
                                    <FaTerminal />
                                    Drishti Telemetry Trace Monitor
                                </span>
                                <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-ping"></span>
                            </div>
                            <div className="font-mono text-[10px] text-green-400 space-y-2 overflow-y-auto max-h-[220px] custom-scrollbar">
                                {terminalLogs.map((log, idx) => (
                                    <div key={idx} className="whitespace-pre-wrap">{log}</div>
                                ))}
                            </div>
                        </div>
                        <button 
                            onClick={() => setTerminalLogs(["Cleared. Awaiting Operator Action..."])}
                            className="w-full py-2 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-bold text-gray-400 hover:text-white transition-colors mt-4"
                        >
                            Reset Console Logs
                        </button>
                    </div>
                </div>

            </div>

            {/* B1. ROLE HIERARCHY MODEL (INTERACTIVE GRID) */}
            <div className="glass-panel p-5 sm:p-6 rounded-2xl border border-white/10 bg-black/40">
                <h4 className="text-sm font-bold uppercase tracking-wider text-orange-400 mb-4 flex items-center gap-2">
                    <FaUserTie className="text-xs" />
                    TANTRA Role Hierarchy & Ownership Matrix
                </h4>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Role selections (Left Column) */}
                    <div className="lg:col-span-4 flex flex-col gap-2 max-h-[300px] overflow-y-auto pr-1 no-scrollbar">
                        {Object.keys(ROLES_METADATA).map(role => {
                            const isSelected = selectedRole === role;
                            return (
                                <div
                                    key={role}
                                    onClick={() => setSelectedRole(role)}
                                    className={`p-3 rounded-xl border text-xs font-bold cursor-pointer transition-all duration-300 flex justify-between items-center ${
                                        isSelected 
                                            ? 'bg-gradient-to-r from-orange-600/20 to-amber-600/20 border-orange-500/40 text-white' 
                                            : 'bg-white/5 border-transparent text-gray-300 hover:bg-white/10 hover:text-white'
                                    }`}
                                >
                                    <span>{role}</span>
                                    <FaChevronRight className={`text-[10px] transition-transform ${isSelected ? 'translate-x-1 text-orange-500' : ''}`} />
                                </div>
                            );
                        })}
                    </div>

                    {/* Role detailed mappings (Right Columns) */}
                    <div className="lg:col-span-8 p-5 rounded-2xl bg-white/5 border border-white/5 flex flex-col justify-between">
                        <div>
                            <div className="text-[10px] font-bold text-orange-400 font-mono tracking-wider mb-1">TANTRA NODE IDENTIFIER</div>
                            <h5 className="text-base font-bold text-white mb-4">{ROLES_METADATA[selectedRole].title}</h5>
                            
                            <div className="space-y-4">
                                <div>
                                    <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Signal Ownership (Telemetry)</div>
                                    <p className="text-xs text-gray-300">{ROLES_METADATA[selectedRole].signals}</p>
                                </div>
                                <div>
                                    <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Visibility Ownership (Data Access Scope)</div>
                                    <p className="text-xs text-gray-300">{ROLES_METADATA[selectedRole].visibility}</p>
                                </div>
                                <div>
                                    <div className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">Action Ownership (Authority Controls)</div>
                                    <p className="text-xs text-gray-300">{ROLES_METADATA[selectedRole].actions}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* B4 & B5. REALITY MAP AND ARCHITECTURAL notes (Bottom Grid) */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Implemented Reality Map */}
                <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-black/30 flex flex-col justify-between">
                    <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-orange-400 mb-4 flex items-center gap-2">
                            <FaMapMarkedAlt className="text-xs" />
                            B5. Implemented Reality Map
                        </h4>
                        
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-[11px] text-gray-300 font-semibold border-collapse">
                                <thead>
                                    <tr className="border-b border-white/10 text-gray-500 text-[9px] uppercase tracking-wider font-bold">
                                        <th className="pb-2">Capability Area</th>
                                        <th className="pb-2">Verification Status</th>
                                        <th className="pb-2">Reality Context</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    <tr>
                                        <td className="py-2.5">Balbharati RAG Ingest</td>
                                        <td className="py-2.5 text-green-400 font-bold">IMPLEMENTED</td>
                                        <td className="py-2.5 text-gray-500">Expanded seeding across Standards 6-10 (Marathi & English).</td>
                                    </tr>
                                    <tr>
                                        <td className="py-2.5">Syllabus Resolution</td>
                                        <td className="py-2.5 text-green-400 font-bold">IMPLEMENTED</td>
                                        <td className="py-2.5 text-gray-500">Strict dynamic metadata `$and` index matches complete.</td>
                                    </tr>
                                    <tr>
                                        <td className="py-2.5">MDU Dashboard UI</td>
                                        <td className="py-2.5 text-green-400 font-bold">IMPLEMENTED</td>
                                        <td className="py-2.5 text-gray-500">Premium glassmorphic lineages & failure simulations.</td>
                                    </tr>
                                    <tr>
                                        <td className="py-2.5">Drishti Foundation</td>
                                        <td className="py-2.5 text-green-400 font-bold">IMPLEMENTED</td>
                                        <td className="py-2.5 text-gray-500">6 Card primitives, 3 prototypes, and 8 role models.</td>
                                    </tr>
                                    <tr>
                                        <td className="py-2.5">Sovereign Voice</td>
                                        <td className="py-2.5 text-amber-400 font-bold">PARTIAL</td>
                                        <td className="py-2.5 text-gray-500">TTS XTTS model falls back to public Google gTTS on timeout.</td>
                                    </tr>
                                    <tr>
                                        <td className="py-2.5">Self-Healing Watchdog</td>
                                        <td className="py-2.5 text-green-400 font-bold">IMPLEMENTED</td>
                                        <td className="py-2.5 text-gray-500">Watchdog server auto-restarts active services on crash.</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* School vs Higher Education Architectural note */}
                <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-black/30 flex flex-col justify-between">
                    <div>
                        <h4 className="text-xs font-bold uppercase tracking-wider text-orange-400 mb-4 flex items-center gap-2">
                            <FaShieldAlt className="text-xs" />
                            B4. School vs. Higher-Ed Architectural Separation
                        </h4>
                        
                        <div className="p-4 rounded-xl bg-black/60 border border-white/5 font-mono text-[9px] text-gray-400 leading-relaxed space-y-4">
                            <div>
                                <span className="text-cyan-400 font-bold">┌────────────────────────────────────────────────────────┐</span>{"\n"}
                                <span className="text-cyan-400 font-bold">│        SHARED INFRASTRUCTURE LAYERS (TANTRA)           │</span>{"\n"}
                                <span className="text-cyan-400 font-bold">└────────────────────────────────────────────────────────┘</span>{"\n"}
                                <span> - Pravah Telemetry Handlers | PRANA Event Gateway | sentence-transformer</span>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-4 pt-2 border-t border-white/5">
                                <div>
                                    <span className="text-orange-400 font-bold">[SCHOOL EDUCATION LAYER]</span>
                                    <ul className="list-disc pl-3 mt-1 space-y-1">
                                        <li>Standard Relational (SQLite users/milestones)</li>
                                        <li>Dynamic K-12 vector namespaces</li>
                                        <li>8 TANTRA Role hierarchies</li>
                                    </ul>
                                </div>
                                <div>
                                    <span className="text-purple-400 font-bold">[HIGHER EDUCATION LAYER]</span>
                                    <ul className="list-disc pl-3 mt-1 space-y-1">
                                        <li>Autonomous LMS indices (Qdrant namespaces)</li>
                                        <li>Higher-Ed Cognitive state models</li>
                                        <li>Custom micro-topic structures</li>
                                    </ul>
                                </div>
                            </div>
                            <div className="pt-2 border-t border-white/5 text-emerald-400 italic">
                                ➔ Multi-tenant databases strictly partitioned. Careless mergers blocked by boundary routers.
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default GurukulDrishti;
