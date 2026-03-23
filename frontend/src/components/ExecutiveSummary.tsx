import React from 'react';
import { Zap } from 'lucide-react';

interface ExecutiveSummaryProps {
  summary: string;
}

export default function ExecutiveSummary({ summary }: ExecutiveSummaryProps) {
  return (
    <div className="glass p-8 rounded-2xl border border-slate-700/50 flex flex-col h-full">
      <h3 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
        <Zap className="w-5 h-5 text-amber-500" />
        AI Executive Intelligence
      </h3>
      <div className="flex-1 bg-slate-900/30 rounded-xl border border-slate-800/50 p-6">
        <p className="text-slate-300 leading-relaxed text-sm">
          {summary || "Analyzing latest environment telemetry and threat landscape..."}
        </p>
      </div>
      <div className="mt-6 flex items-center gap-3 text-xs text-slate-500 italic">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
        Grounded in Policy & Governance Frameworks
      </div>
    </div>
  );
}
