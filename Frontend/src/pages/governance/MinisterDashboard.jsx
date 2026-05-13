import React, { useState, useEffect } from 'react';
import GovernanceLayout from '../../components/governance/GovernanceLayout';
import SignalCard from '../../components/governance/SignalCard';
import AlertFeed from '../../components/governance/AlertFeed';
import ActionButton from '../../components/governance/ActionButton';
import { ShieldAlert, Globe, Activity, BarChart3, Rocket, MessageSquare, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../../config';

const MinisterDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/system/metrics`);
        const data = await response.json();
        setMetrics(data);
        
        // Map watchdog events to alert feed format
        if (data.watchdog && data.watchdog.recent_recovery_events) {
          const mappedAlerts = data.watchdog.recent_recovery_events.map(event => ({
            title: `${event.service} ${event.event}`,
            message: event.detail,
            time: event.timestamp.split('T')[1].split('.')[0], // Simple time format
            type: event.event.includes('FAILURE') ? 'anomaly' : 'pattern',
            trace_id: `TR-${event.service.substring(0, 3).toUpperCase()}-${Math.floor(Math.random() * 9000) + 1000}`,
            priority: event.event.includes('CRITICAL') ? 'High' : 'Low'
          })).reverse();
          setAlerts(mappedAlerts);
        }
      } catch (error) {
        console.error("Failed to fetch governance metrics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const getSystemHealth = () => {
    if (!metrics) return "Connecting...";
    return metrics.status === "healthy" ? "Healthy" : "Degraded";
  };

  return (
    <GovernanceLayout level="Minister" healthStatus={getSystemHealth()}>
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Top Metrics */}
        <div className="lg:col-span-3 space-y-6">
          <SignalCard 
            title="System Uptime"
            value={metrics ? metrics.uptime_human : "0s"}
            signal={metrics?.status === "healthy" ? "healthy" : "risk"}
            trend="up"
            description="Continuous runtime of the Gurukul TANTRA core."
          />
          <SignalCard 
            title="Request Throughput"
            value={metrics ? metrics.requests.total : "0"}
            unit="req"
            signal="healthy"
            trend={metrics?.requests.total > 100 ? "up" : "neutral"}
            description="Real-time HTTP signal ingestion volume."
          />
          <SignalCard 
            title="Error Rate"
            value={metrics ? metrics.requests.error_rate_percent : "0"}
            unit="%"
            signal={metrics?.requests.error_rate_percent > 5 ? "risk" : "healthy"}
            trend={metrics?.requests.error_rate_percent > 0 ? "up" : "down"}
            description="Systemic variance detected in runtime execution."
          />
        </div>

        {/* Middle Column: Intelligence Heatmap & System Pulse */}
        <div className="lg:col-span-6 space-y-6">
          {/* Main Heatmap Placeholder */}
          <div className="relative rounded-3xl border border-white/10 bg-white/5 overflow-hidden aspect-[16/10] flex flex-col group">
            <div className="p-6 border-b border-white/5 bg-white/[0.02] flex justify-between items-center">
              <div>
                <h3 className="font-bold text-white text-lg tracking-tight">Macro System Health</h3>
                <p className="text-xs text-gray-500">Real-time educational signals across the country</p>
              </div>
              <div className="flex gap-2">
                <button className="px-3 py-1 rounded-lg bg-white/10 text-[10px] font-bold text-white uppercase tracking-wider">Heatmap</button>
                <button className="px-3 py-1 rounded-lg bg-white/5 text-[10px] font-bold text-gray-500 uppercase tracking-wider hover:text-white transition-colors">Satellite</button>
              </div>
            </div>
            
            <div className="flex-1 flex items-center justify-center relative p-8">
              {/* Visual representation of a heatmap/map */}
              <div className="w-full h-full rounded-2xl bg-[#0a0a0a] border border-white/5 relative overflow-hidden flex items-center justify-center">
                <Globe className={metrics?.status === "healthy" ? "text-accent/20 animate-pulse" : "text-red-500/20 animate-bounce"} size={300} />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-transparent opacity-60" />
                
                {/* Simulated Data Points based on real health */}
                {metrics?.status === "healthy" ? (
                   <div className="absolute bottom-1/3 right-1/4 h-6 w-6 bg-emerald-500 rounded-full blur-[12px] opacity-40 animate-pulse" />
                ) : (
                   <div className="absolute top-1/4 left-1/3 h-4 w-4 bg-red-500 rounded-full blur-[8px] animate-ping" />
                )}
                <div className="absolute top-1/2 right-1/3 h-3 w-3 bg-yellow-500 rounded-full blur-[6px] animate-pulse" />
              </div>
              
              {/* Legend */}
              <div className="absolute bottom-12 right-12 p-3 rounded-xl bg-black/80 backdrop-blur-md border border-white/10 text-[10px] font-bold uppercase space-y-2">
                <div className="flex items-center gap-2 text-emerald-500">
                  <div className="h-2 w-2 rounded-full bg-emerald-500" /> High Performance
                </div>
                <div className="flex items-center gap-2 text-yellow-500">
                  <div className="h-2 w-2 rounded-full bg-yellow-500" /> Signal Variance
                </div>
                <div className="flex items-center gap-2 text-red-500">
                  <div className="h-2 w-2 rounded-full bg-red-500" /> Systemic Risk
                </div>
              </div>
            </div>
          </div>

          {/* Secondary Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-5 rounded-2xl border border-white/10 bg-white/5">
              <div className="flex items-center gap-2 text-gray-500 mb-2">
                <Activity size={14} />
                <span className="text-[10px] font-bold uppercase tracking-widest">CPU Usage</span>
              </div>
              <div className="text-xl font-bold text-white">{metrics ? `${metrics.system.resource_usage.cpu_percent}%` : "0%"}</div>
              <div className="w-full bg-white/5 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-emerald-500 h-full transition-all duration-500" style={{ width: metrics ? `${metrics.system.resource_usage.cpu_percent}%` : "0%" }} />
              </div>
            </div>
            <div className="p-5 rounded-2xl border border-white/10 bg-white/5">
              <div className="flex items-center gap-2 text-gray-500 mb-2">
                <BarChart3 size={14} />
                <span className="text-[10px] font-bold uppercase tracking-widest">Memory Usage</span>
              </div>
              <div className="text-xl font-bold text-white">{metrics ? `${metrics.system.resource_usage.memory_percent}%` : "0%"}</div>
              <div className="w-full bg-white/5 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-accent h-full transition-all duration-500" style={{ width: metrics ? `${metrics.system.resource_usage.memory_percent}%` : "0%" }} />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Alerts & Actions */}
        <div className="lg:col-span-3 space-y-6">
          <AlertFeed alerts={alerts.length > 0 ? alerts : [{title: "System Nominal", message: "No anomalies detected in last cycle.", time: "now", type: "info", trace_id: "GURUKUL-SYS", priority: "Low"}]} />
          
          <div className="space-y-3">
            <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest ml-1 mb-2">Action Layer</h4>
            <ActionButton 
              label="Policy Action" 
              subLabel="Draft new structural reforms" 
              icon={Rocket}
              variant="accent"
              onClick={() => alert("Policy Action Triggered - Trace: " + (metrics?.watchdog?.uptime_s || "sys"))}
            />
            <ActionButton 
              label="Emergency Esc" 
              subLabel="Critical escalation to Cabinet" 
              icon={ShieldAlert}
              variant="danger"
              onClick={() => alert("Emergency Escalation Triggered")}
            />
            <ActionButton 
              label="Public Address" 
              subLabel="Schedule system update broadcast" 
              icon={MessageSquare}
              variant="primary"
              onClick={() => alert("Public Address Scheduled")}
            />
          </div>
        </div>

      </div>
    </GovernanceLayout>
  );
};

export default MinisterDashboard;

export default MinisterDashboard;
