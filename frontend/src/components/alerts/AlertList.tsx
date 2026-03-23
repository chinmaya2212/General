"use client";

import React from 'react';
import { ShieldAlert, Clock, Terminal } from 'lucide-react';
import { Alert } from '@/lib/types';

interface AlertListProps {
  alerts: Alert[];
  selectedId: string | null;
  onSelect: (alert: Alert) => void;
}

export default function AlertList({ alerts, selectedId, onSelect }: AlertListProps) {
  return (
    <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
      {alerts.length > 0 ? (
        alerts.map((alert) => (
          <button
            key={alert.id}
            onClick={() => onSelect(alert)}
            className={`w-full text-left p-4 rounded-xl border transition-all hover:scale-[1.01] active:scale-[0.99] ${
              selectedId === alert.id 
              ? 'glass border-blue-500/50 ring-1 ring-blue-500/30' 
              : 'bg-slate-900/40 border-slate-700/50 hover:bg-slate-800/40'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                alert.severity === 'critical' ? 'bg-rose-500/20 text-rose-500' : 'bg-slate-800 text-slate-400'
              }`}>{alert.severity}</span>
              <span className="text-[10px] text-slate-500 flex items-center gap-1">
                <Clock className="w-3 h-3" /> {new Date(alert.created_at).toLocaleDateString()}
              </span>
            </div>
            <h4 className="font-semibold text-white text-sm line-clamp-1 mb-1">{alert.name}</h4>
            <div className="flex items-center gap-3">
               <span className="text-[10px] text-slate-500 flex items-center gap-1">
                 <Terminal className="w-3 h-3" /> {alert.source}
               </span>
               <span className="text-[10px] text-slate-500 bg-slate-800/50 px-1.5 rounded">{alert.status}</span>
            </div>
          </button>
        ))
      ) : (
        <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-40">
           <ShieldAlert className="w-10 h-10 mb-2" />
           <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">No Alerts Found</p>
        </div>
      )}
    </div>
  );
}
