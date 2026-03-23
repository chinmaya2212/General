"use client";

import React, { useState } from 'react';
import { 
  FileLock2, 
  Search, 
  Clock, 
  Loader2, 
  Network, 
  History, 
  FileText,
  AlertCircle
} from 'lucide-react';
import { Incident } from '@/lib/types';
import { apiClient } from '@/lib/api-client';

interface IncidentDetailProps {
  incident: Incident;
}

export default function IncidentDetail({ incident }: IncidentDetailProps) {
  const [investigation, setInvestigation] = useState<any>(null);
  const [isInvestigating, setIsInvestigating] = useState(false);

  const handleInvestigate = async () => {
    setIsInvestigating(true);
    try {
      const result = await apiClient.runInvestigation(incident.id);
      setInvestigation(result.output);
    } catch (error) {
      console.error('Investigation failed:', error);
    } finally {
      setIsInvestigating(false);
    }
  };

  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-right-4 duration-500">
      <div className="glass p-6 rounded-2xl border border-slate-700/50 space-y-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-500 text-[10px] font-bold uppercase tracking-wider">{incident.severity}</span>
              <span className="text-[10px] font-medium text-slate-500">{incident.status}</span>
            </div>
            <h3 className="text-xl font-bold text-white leading-tight">{incident.name}</h3>
          </div>
          <button 
            onClick={handleInvestigate}
            disabled={isInvestigating}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition-all shadow-lg shadow-purple-600/20 active:scale-[0.98] disabled:opacity-50"
          >
            {isInvestigating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
            Investigate with AI
          </button>
        </div>
      </div>

      <div className="flex-1 space-y-8 overflow-y-auto pr-2 custom-scrollbar">
        {investigation ? (
          <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-700">
            <section className="space-y-4">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <History className="w-3.5 h-3.5 text-purple-400" /> Investigation Narrative
              </h4>
              <div className="glass p-6 rounded-2xl border border-slate-700/50">
                 <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{investigation.narrative}</p>
              </div>
            </section>

            <section className="space-y-4">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-blue-400" /> Event Timeline
              </h4>
              <div className="space-y-4 relative before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-slate-800">
                {(investigation.timeline || []).map((step: any, i: number) => (
                  <div key={i} className="relative pl-8 group">
                    <div className="absolute left-0 top-1.5 w-6 h-6 rounded-full bg-slate-900 border-2 border-slate-700 flex items-center justify-center group-hover:border-blue-500 transition-all z-10">
                       <div className="w-1.5 h-1.5 rounded-full bg-slate-600 group-hover:bg-blue-500 transition-all"></div>
                    </div>
                    <div className="glass p-4 rounded-xl border border-slate-800/50 group-hover:border-slate-700 transition-all">
                       <p className="text-[10px] font-bold text-slate-500 mb-1">{step.timestamp}</p>
                       <p className="text-sm text-slate-300">{step.summary}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section className="space-y-4">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <Network className="w-3.5 h-3.5 text-emerald-400" /> Correlated Evidence
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {(investigation.evidence || []).map((ev: any, i: number) => (
                  <div key={i} className="glass p-4 rounded-xl border border-slate-800/50 flex gap-3">
                    <div className="p-2 rounded-lg bg-slate-800/50 h-fit">
                       <FileText className="w-4 h-4 text-emerald-500" />
                    </div>
                    <div className="space-y-1">
                       <p className="text-xs font-bold text-white leading-tight">{ev.type}</p>
                       <p className="text-[10px] text-slate-500 truncate">{ev.value}</p>
                       <p className="text-[10px] text-slate-400 italic">Confidence: {ev.confidence}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center p-12 glass rounded-2xl border-dashed opacity-40 grayscale space-y-4">
            <FileLock2 className="w-12 h-12 text-slate-600" />
            <div className="space-y-1">
              <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Investigation Pending</p>
              <p className="text-xs text-slate-600 max-w-[200px]">Launch the AI Investigation Agent to trace attack paths and build a narrative timeline.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
