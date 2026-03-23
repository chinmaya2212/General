"use client";

import React, { useState } from 'react';
import { 
  ShieldAlert, 
  Terminal, 
  ChevronRight, 
  Loader2, 
  Zap, 
  CheckCircle2, 
  AlertTriangle,
  ExternalLink
} from 'lucide-react';
import { Alert } from '@/lib/types';
import { apiClient } from '@/lib/api-client';

interface AlertDetailProps {
  alert: Alert;
  onUpdate?: () => void;
}

export default function AlertDetail({ alert, onUpdate }: AlertDetailProps) {
  const [triageResult, setTriageResult] = useState<any>(null);
  const [isTriaging, setIsTriaging] = useState(false);

  const handleTriage = async () => {
    setIsTriaging(true);
    try {
      const result = await apiClient.runTriage(alert.id);
      setTriageResult(result.output);
    } catch (error) {
      console.error('Triage failed:', error);
    } finally {
      setIsTriaging(false);
    }
  };

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-right-4 duration-500">
      <div className="glass p-6 rounded-2xl border border-slate-700/50 space-y-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                alert.severity === 'critical' ? 'bg-rose-500/20 text-rose-500' : 'bg-slate-800 text-slate-400'
              }`}>{alert.severity}</span>
              <span className="text-[10px] font-medium text-slate-500">ID: {alert.id}</span>
            </div>
            <h3 className="text-xl font-bold text-white leading-tight">{alert.name}</h3>
          </div>
          <button 
            onClick={handleTriage}
            disabled={isTriaging}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all shadow-lg shadow-blue-600/20 active:scale-[0.98] disabled:opacity-50"
          >
            {isTriaging ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
            Run AI Triage
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-700/30">
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Source System</p>
            <p className="text-sm text-slate-300 flex items-center gap-1.5"><Terminal className="w-3.5 h-3.5 text-blue-500" /> {alert.source}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Timestamp</p>
            <p className="text-sm text-slate-300">{new Date(alert.created_at).toLocaleString()}</p>
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto pr-2 custom-scrollbar">
        {triageResult ? (
          <div className="space-y-6 animate-in zoom-in-95 duration-500">
            <div className="glass p-6 rounded-2xl border border-blue-500/30 bg-blue-500/5 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-3 opacity-10">
                  <Zap className="w-12 h-12 text-blue-500" />
               </div>
               <h4 className="text-sm font-bold text-blue-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                 <CheckCircle2 className="w-4 h-4" /> AI Triage Assessment
               </h4>
               <div className="space-y-4">
                  <div className="flex gap-4">
                    <div className="w-1 h-auto bg-blue-500/30 rounded-full"></div>
                    <div className="flex-1 space-y-1">
                       <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Recommended Severity</p>
                       <p className="text-lg font-bold text-white capitalize">{triageResult.estimated_priority || 'N/A'}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">Analysis Rationale</p>
                    <p className="text-sm text-slate-300 leading-relaxed">{triageResult.summary}</p>
                  </div>
               </div>
            </div>

            <div className="glass p-6 rounded-2xl border border-slate-700/50 space-y-4">
               <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500" /> Next Investigative Actions
               </h4>
               <div className="space-y-2">
                  {(triageResult.next_steps || []).map((step: string, i: number) => (
                    <div key={i} className="flex gap-3 p-3 rounded-lg bg-slate-900/50 border border-slate-800 group hover:border-slate-700 transition-all">
                       <div className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-400 shrink-0 group-hover:bg-blue-600 group-hover:text-white transition-all">
                          {i + 1}
                       </div>
                       <p className="text-xs text-slate-400 leading-normal">{step}</p>
                    </div>
                  ))}
               </div>
            </div>
            
            <button className="w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 transition-all flex items-center justify-center gap-2">
               Open Investigation Narrative <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center p-12 glass rounded-2xl border-dashed opacity-40 grayscale space-y-4">
            <Zap className="w-12 h-12 text-slate-600" />
            <div className="space-y-1">
              <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Triage Pending</p>
              <p className="text-xs text-slate-600 max-w-[200px]">Run the AI Triage Agent to enrich this alert with environmental context.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
