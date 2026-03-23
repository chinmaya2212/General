"use client";

import { useState, useEffect } from 'react';
import { 
  Settings, 
  Activity, 
  Database, 
  Zap, 
  RefreshCcw, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle,
  Loader2,
  Lock,
  Cpu
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { useAuth } from '@/context/AuthContext';

export default function SettingsPage() {
  const { user } = useAuth();
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    async function fetchStatus() {
      try {
        const data = await apiClient.getSystemStatus();
        setStatus(data);
      } catch (error) {
        console.error('Failed to fetch system status:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchStatus();
  }, []);

  const handleAction = async (action: string) => {
    setActionLoading(action);
    try {
      await apiClient.runAdminAction(action);
      // Wait a bit to simulate processing
      await new Promise(r => setTimeout(r, 1500));
    } catch (error) {
      console.error(`Action ${action} failed:`, error);
    } finally {
      setActionLoading(null);
    }
  };

  const connectors = [
    { name: 'Core Backend', id: 'backend', icon: Activity },
    { name: 'MongoDB Knowledge Base', id: 'mongodb', icon: Database },
    { name: 'MISP Threat Intel', id: 'misp', icon: ShieldAlert },
    { name: 'CISO Assistant API', id: 'ciso', icon: Zap },
    { name: 'Vertex AI / Gemini', id: 'llm', icon: Cpu },
  ];

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-end justify-between">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight text-white glow-text">System Configuration</h2>
          <p className="text-slate-400">Monitor connector health and manage platform maintenance hooks.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800">
           <div className={`w-2 h-2 rounded-full ${status ? 'bg-emerald-500 animate-pulse' : 'bg-slate-700'}`}></div>
           <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{status ? 'System Online' : 'Checking Connectivity...'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1 min-h-0">
        <div className="lg:col-span-2 space-y-8 overflow-y-auto custom-scrollbar pr-2">
           <section className="space-y-4">
              <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-500" /> Infrastructure Connectors
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 {connectors.map((c) => {
                   const Icon = c.icon;
                   const isConnected = status?.[c.id]?.status === 'connected' || status?.[c.id] === true;
                   return (
                     <div key={c.id} className="glass p-5 rounded-2xl border border-slate-800/50 flex items-center justify-between group hover:border-slate-700/50 transition-all">
                        <div className="flex items-center gap-4">
                           <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 group-hover:bg-slate-800 transition-all">
                              <Icon className="w-5 h-5 text-slate-400" />
                           </div>
                           <div>
                              <p className="text-sm font-bold text-slate-200">{c.name}</p>
                              <p className="text-[10px] text-slate-500 uppercase font-medium">{isConnected ? 'Operational' : 'Disconnected'}</p>
                           </div>
                        </div>
                        {isConnected ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                        ) : (
                          <XCircle className="w-5 h-5 text-rose-500" />
                        )}
                     </div>
                   );
                 })}
              </div>
           </section>

           <section className="space-y-4 pt-4">
              <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Settings className="w-4 h-4 text-slate-400" /> Platform Preferences
              </h3>
              <div className="glass p-6 rounded-3xl border border-slate-800/50 space-y-6">
                 <div className="flex items-center justify-between">
                    <div className="space-y-1">
                       <p className="text-sm font-medium text-slate-200">Real-time Triage</p>
                       <p className="text-xs text-slate-500">Enable automatic background triage of incoming high-severity alerts.</p>
                    </div>
                    <div className="w-10 h-6 rounded-full bg-blue-600 relative">
                       <div className="absolute right-1 top-1 w-4 h-4 rounded-full bg-white shadow-sm"></div>
                    </div>
                 </div>
                 <div className="h-px bg-slate-800/50"></div>
                 <div className="flex items-center justify-between">
                    <div className="space-y-1">
                       <p className="text-sm font-medium text-slate-200">Grounded Reasoning</p>
                       <p className="text-xs text-slate-500">Require citations for all AI generated summaries and recommendations.</p>
                    </div>
                    <div className="w-10 h-6 rounded-full bg-slate-800">
                       <div className="absolute left-1 top-1 w-4 h-4 rounded-full bg-slate-600 shadow-sm"></div>
                    </div>
                 </div>
              </div>
           </section>
        </div>

        <div className="space-y-6">
           <div className={`glass p-8 rounded-3xl border ${isAdmin ? 'border-amber-500/20 bg-amber-500/5' : 'border-slate-800/50 opacity-40 grayscale'} flex flex-col h-full`}>
              <div className="flex items-center gap-3 mb-8">
                 <div className={`p-2 rounded-lg ${isAdmin ? 'bg-amber-500' : 'bg-slate-700'}`}>
                    <Lock className="w-5 h-5 text-white" />
                 </div>
                 <h3 className="text-xl font-bold text-white tracking-tight">Admin Console</h3>
              </div>

              {!isAdmin && (
                <div className="flex-1 flex flex-col items-center justify-center text-center space-y-2 p-4">
                   <ShieldAlert className="w-10 h-10 text-slate-600 mb-2" />
                   <p className="text-xs font-bold text-slate-500 uppercase tracking-widest leading-relaxed">Administrator Privileges Required</p>
                </div>
              )}

              {isAdmin && (
                <div className="flex-1 space-y-4">
                   {[
                     { id: 'seed_load', label: 'Reload Seed Foundation', desc: 'Sync baseline knowledge and entities.' },
                     { id: 'sync_jobs', label: 'Trigger Connector Sync', desc: 'Force immediate poll of MISP/CISO.' },
                     { id: 'rebuild_graph', label: 'Reconcile Knowledge Graph', desc: 'Recalculate all entity relationships.' },
                     { id: 'rebuild_vectors', label: 'Re-index Vector Store', desc: 'Refresh embeddings for all documents.' },
                   ].map((a) => (
                     <button
                       key={a.id}
                       disabled={!!actionLoading}
                       onClick={() => handleAction(a.id)}
                       className="w-full text-left p-4 rounded-2xl bg-slate-900 border border-slate-800 hover:border-amber-500/50 hover:bg-slate-800 transition-all group flex items-start gap-4 disabled:opacity-50"
                     >
                       <div className="p-2 rounded-lg bg-slate-800 border border-slate-700 group-hover:bg-amber-500/10 group-hover:border-amber-500/20 transition-all shrink-0 mt-1">
                          {actionLoading === a.id ? <Loader2 className="w-4 h-4 text-amber-500 animate-spin" /> : <RefreshCcw className="w-4 h-4 text-slate-500 group-hover:text-amber-500" />}
                       </div>
                       <div className="space-y-1">
                          <p className="text-sm font-bold text-slate-200 group-hover:text-white">{a.label}</p>
                          <p className="text-[10px] text-slate-500 leading-normal">{a.desc}</p>
                       </div>
                     </button>
                   ))}
                </div>
              )}
              
              <div className="mt-8 pt-6 border-t border-slate-800/50">
                 <p className="text-[10px] text-slate-500 leading-relaxed italic">Operational actions are logged and audited. Use with caution during production windows.</p>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
