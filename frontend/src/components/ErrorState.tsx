"use client";

import { AlertCircle, RefreshCcw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export default function ErrorState({ 
  title = "Telemetry Interrupted", 
  message = "We encountered an issue while fetching data from the security core.",
  onRetry 
}: ErrorStateProps) {
  return (
    <div className="flex-1 glass rounded-3xl border-rose-500/20 flex flex-col items-center justify-center text-center p-12 space-y-6 animate-in zoom-in-95 duration-500 min-h-[400px]">
      <div className="p-4 rounded-full bg-rose-500/10 border border-rose-500/20">
        <AlertCircle className="w-12 h-12 text-rose-500" />
      </div>
      <div className="space-y-2 max-w-sm">
        <h3 className="text-xl font-bold text-white tracking-tight">{title}</h3>
        <p className="text-sm text-slate-400 leading-relaxed">{message}</p>
      </div>
      {onRetry && (
        <button 
          onClick={onRetry}
          className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-300 hover:text-white hover:border-slate-600 transition-all font-bold text-xs uppercase tracking-widest active:scale-[0.98]"
        >
          <RefreshCcw className="w-3.5 h-3.5" /> Retry Sync
        </button>
      )}
    </div>
  );
}
