"use client";

import React from 'react';
import { FileLock2, Clock, User } from 'lucide-react';
import { Incident } from '@/lib/types';

interface IncidentListProps {
  incidents: Incident[];
  selectedId: string | null;
  onSelect: (incident: Incident) => void;
}

export default function IncidentList({ incidents, selectedId, onSelect }: IncidentListProps) {
  return (
    <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
      {incidents.length > 0 ? (
        incidents.map((incident) => (
          <button
            key={incident.id}
            onClick={() => onSelect(incident)}
            className={`w-full text-left p-4 rounded-xl border transition-all hover:scale-[1.01] active:scale-[0.99] ${
              selectedId === incident.id 
              ? 'glass border-purple-500/50 ring-1 ring-purple-500/30 shadow-lg shadow-purple-500/5' 
              : 'bg-slate-900/40 border-slate-700/50 hover:bg-slate-800/40'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-500`}>
                {incident.severity}
              </span>
              <span className="text-[10px] text-slate-500 flex items-center gap-1">
                <Clock className="w-3 h-3" /> {new Date(incident.created_at).toLocaleDateString()}
              </span>
            </div>
            <h4 className="font-semibold text-white text-sm line-clamp-1 mb-2">{incident.name}</h4>
            <div className="flex items-center justify-between mt-auto">
               <span className="text-[10px] text-slate-400 bg-slate-800 rounded px-1.5 py-0.5">{incident.status}</span>
               <div className="flex items-center gap-1 text-[10px] text-slate-500">
                  <User className="w-3 h-3" /> SecOps Analyst
               </div>
            </div>
          </button>
        ))
      ) : (
        <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-40">
           <FileLock2 className="w-10 h-10 mb-2" />
           <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">No Active Incidents</p>
        </div>
      )}
    </div>
  );
}
