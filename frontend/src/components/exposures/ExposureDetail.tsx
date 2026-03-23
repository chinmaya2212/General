"use client";

import React from 'react';
import { 
  Radar, 
  ShieldCheck, 
  Globe, 
  Zap, 
  AlertCircle, 
  Network, 
  Activity,
  ArrowRight
} from 'lucide-react';
import { Exposure } from '@/lib/types';

interface ExposureDetailProps {
  exposure: Exposure;
}

export default function ExposureDetail({ exposure }: ExposureDetailProps) {
  return (
    <div className="space-y-6 h-full flex flex-col animate-in fade-in slide-in-from-right-4 duration-500">
      <div className="glass p-6 rounded-2xl border border-blue-500/30 bg-blue-500/5 space-y-4">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h3 className="text-xl font-bold text-white leading-tight">{exposure.asset_name}</h3>
            <p className="text-[10px] font-medium text-slate-500 uppercase tracking-widest">Asset ID: {exposure.asset_id}</p>
          </div>
          <div className="text-right">
             <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-1">Exposure Score</p>
             <p className="text-3xl font-bold text-white tabular-nums">{exposure.base_score}</p>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4 pt-4 border-t border-slate-700/30">
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Criticality</p>
            <p className="text-sm text-slate-300">Factor: {exposure.metrics.criticality_factor}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Reachability</p>
            <p className={`text-sm flex items-center gap-1 ${exposure.metrics.is_reachable ? 'text-amber-500' : 'text-emerald-500'}`}>
               <Globe className="w-3.5 h-3.5" /> {exposure.metrics.is_reachable ? 'External' : 'Internal'}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Highest CVSS</p>
            <p className="text-sm text-slate-300 font-mono">{exposure.metrics.max_cvss}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Privilege Risk</p>
            <p className={`text-sm ${exposure.metrics.privilege_risk ? 'text-rose-500' : 'text-slate-500'}`}>
               {exposure.metrics.privilege_risk ? 'High' : 'Low'}
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-8 overflow-y-auto pr-2 custom-scrollbar">
        <section className="space-y-4">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-blue-400" /> Exposure Rationale
          </h4>
          <div className="space-y-2">
            {(exposure.rationale || []).map((reason, i) => (
              <div key={i} className="flex gap-3 p-3 rounded-xl bg-slate-900/40 border border-slate-800/50">
                <AlertCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                <p className="text-xs text-slate-300 leading-normal">{reason}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Hardening Guidance
          </h4>
          <div className="grid grid-cols-1 gap-3">
            {(exposure.remediation_plan || []).map((step, i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 group hover:border-emerald-500/40 transition-all">
                <div className="flex items-center gap-4">
                   <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center text-[10px] font-bold text-emerald-500">
                      {i + 1}
                   </div>
                   <p className="text-sm text-emerald-100 font-medium">{step}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-emerald-500 opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0" />
              </div>
            ))}
          </div>
        </section>
        
        <section className="space-y-4">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
            <Network className="w-3.5 h-3.5 text-blue-400" /> Related Entities
          </h4>
          <div className="flex flex-wrap gap-2">
             <span className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-[10px] font-medium text-slate-300 flex items-center gap-2">
                <Activity className="w-3 h-3 text-blue-500" /> Internal Segment
             </span>
             <span className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-[10px] font-medium text-slate-300 flex items-center gap-2">
                <ShieldCheck className="w-3 h-3 text-emerald-500" /> EDR Control
             </span>
          </div>
        </section>
      </div>
    </div>
  );
}
