"use client";

import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  message?: string;
  submessage?: string;
  fullPage?: boolean;
}

export default function LoadingState({ 
  message = "Syncing Intelligence...", 
  submessage = "Contacting the AI Security Core",
  fullPage = false 
}: LoadingStateProps) {
  const content = (
    <div className="flex flex-col items-center justify-center text-center p-12 space-y-6 animate-in fade-in duration-700">
      <div className="relative">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
        <div className="absolute inset-0 w-12 h-12 rounded-full border-2 border-blue-500/20 animate-ping"></div>
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-bold text-white tracking-tight">{message}</h3>
        <p className="text-xs text-slate-500 font-medium uppercase tracking-widest">{submessage}</p>
      </div>
    </div>
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 z-[100] bg-slate-950/80 backdrop-blur-md flex items-center justify-center">
        {content}
      </div>
    );
  }

  return (
    <div className="flex-1 glass rounded-3xl flex items-center justify-center min-h-[400px]">
      {content}
    </div>
  );
}
