"use client";

import React from 'react';
import { Radar, Globe, AlertCircle } from 'lucide-react';
import { Exposure } from '@/lib/types';

interface ExposureListProps {
  exposures: Exposure[];
  selectedId: string | null;
  onSelect: (exposure: Exposure) => void;
}

export default function ExposureList({ exposures, selectedId, onSelect }: ExposureListProps) {
  return (
    <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
      {exposures.length > 0 ? (
        exposures.map((exp) => (
          <button
            key={exp.asset_id}
            onClick={() => onSelect(exp)}
            className={`w-full text-left p-4 rounded-xl border transition-all hover:scale-[1.01] active:scale-[0.99] ${
              selectedId === exp.asset_id 
              ? 'glass border-blue-500/50 ring-1 ring-blue-500/30' 
              : 'bg-slate-900/40 border-slate-700/50 hover:bg-slate-800/40'
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest flex items-center gap-1">
                <Radar className="w-3 h-3" /> Score: {exp.base_score}
              </span>
              {exp.metrics.is_reachable && (
                <Globe className="w-3.5 h-3.5 text-amber-500" />
              )}
            </div>
            <h4 className="font-semibold text-white text-sm line-clamp-1 mb-1">{exp.asset_name}</h4>
            <div className="flex items-center gap-2">
               <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                 exp.metrics.max_cvss >= 9 ? 'bg-rose-500/20 text-rose-500' : 'bg-slate-800 text-slate-500'
               }`}>CVSS {exp.metrics.max_cvss}</span>
               {exp.metrics.privilege_risk && (
                 <span className="text-[9px] text-amber-500 font-bold uppercase tracking-tighter">Privilege Risk</span>
               )}
            </div>
          </button>
        ))
      ) : (
        <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-40">
           <AlertCircle className="w-10 h-10 mb-2" />
           <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">No Exposures Found</p>
        </div>
      )}
    </div>
  );
}
