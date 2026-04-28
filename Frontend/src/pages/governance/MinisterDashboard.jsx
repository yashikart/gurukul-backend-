import React from 'react';
import GovernanceLayout from '../../components/governance/GovernanceLayout';
import SignalCard from '../../components/governance/SignalCard';
import AlertFeed from '../../components/governance/AlertFeed';
import ActionButton from '../../components/governance/ActionButton';
import { ShieldAlert, Globe, Activity, BarChart3, Rocket, MessageSquare, AlertCircle } from 'lucide-react';

const MinisterDashboard = () => {
  const mockAlerts = [
    {
      title: 'State-wide Literacy Drop',
      message: 'Significant anomaly detected in primary literacy signals across 3 districts.',
      time: '12m ago',
      type: 'anomaly',
      trace_id: 'TR-MIN-8821',
      priority: 'High'
    },
    {
      title: 'Policy Impact Positive',
      message: 'Pattern analysis shows 12% increase in vocational enrollment following Q1 reforms.',
      time: '2h ago',
      type: 'pattern',
      trace_id: 'TR-MIN-9042',
      priority: 'Low'
    },
    {
      title: 'Critical Infrastructure Risk',
      message: 'Systemic failure in District C digital connectivity at scale.',
      time: '5h ago',
      type: 'anomaly',
      trace_id: 'TR-MIN-7712',
      priority: 'High'
    }
  ];

  return (
    <GovernanceLayout level="Minister" healthStatus="Healthy">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Top Metrics */}
        <div className="lg:col-span-3 space-y-6">
          <SignalCard 
            title="National Rank"
            value="#04"
            signal="healthy"
            trend="up"
            description="Overall educational performance ranking vs National average."
          />
          <SignalCard 
            title="Literacy Rate"
            value="88.2"
            unit="%"
            signal="risk"
            trend="down"
            description="System-wide literacy signals monitored via TANTRA."
          />
          <SignalCard 
            title="Impact Score"
            value="4.2"
            unit="M"
            signal="healthy"
            trend="up"
            description="Total students reached through systemic policy actions."
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
                <Globe className="text-accent/20 animate-pulse" size={300} />
                <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-transparent opacity-60" />
                
                {/* Simulated Data Points */}
                <div className="absolute top-1/4 left-1/3 h-4 w-4 bg-red-500 rounded-full blur-[8px] animate-ping" />
                <div className="absolute bottom-1/3 right-1/4 h-6 w-6 bg-emerald-500 rounded-full blur-[12px] opacity-40 animate-pulse" />
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
                <span className="text-[10px] font-bold uppercase tracking-widest">Public Sentiment</span>
              </div>
              <div className="text-xl font-bold text-white">72% Positive</div>
              <div className="w-full bg-white/5 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-emerald-500 h-full w-[72%]" />
              </div>
            </div>
            <div className="p-5 rounded-2xl border border-white/10 bg-white/5">
              <div className="flex items-center gap-2 text-gray-500 mb-2">
                <BarChart3 size={14} />
                <span className="text-[10px] font-bold uppercase tracking-widest">Budget Used</span>
              </div>
              <div className="text-xl font-bold text-white">₹ 14,200 Cr</div>
              <div className="w-full bg-white/5 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-accent h-full w-[45%]" />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Alerts & Actions */}
        <div className="lg:col-span-3 space-y-6">
          <AlertFeed alerts={mockAlerts} />
          
          <div className="space-y-3">
            <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest ml-1 mb-2">Action Layer</h4>
            <ActionButton 
              label="Policy Action" 
              subLabel="Draft new structural reforms" 
              icon={Rocket}
              variant="accent"
            />
            <ActionButton 
              label="Emergency Esc" 
              subLabel="Critical escalation to Cabinet" 
              icon={ShieldAlert}
              variant="danger"
            />
            <ActionButton 
              label="Public Address" 
              subLabel="Schedule system update broadcast" 
              icon={MessageSquare}
              variant="primary"
            />
          </div>
        </div>

      </div>
    </GovernanceLayout>
  );
};

export default MinisterDashboard;
