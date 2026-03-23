"use client";

import React, { useState } from 'react';
import { 
  BookOpen, 
  Send, 
  Loader2, 
  Quote, 
  CheckCircle2, 
  HelpCircle 
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

export default function PolicyAdvisor() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const data = await apiClient.askPolicyAdvisor(query);
      setResult(data.output);
    } catch (error) {
      console.error('Policy advice failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass p-8 rounded-2xl border border-blue-500/30 bg-blue-500/5 h-full flex flex-col space-y-6">
      <div className="flex items-center gap-3">
         <div className="p-2 rounded-lg bg-blue-600 shadow-lg shadow-blue-500/20">
            <BookOpen className="w-5 h-5 text-white" />
         </div>
         <h3 className="text-xl font-bold text-white tracking-tight">Policy Advisor</h3>
      </div>

      <form onSubmit={handleAsk} className="relative">
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a governance or framework question..."
          className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl py-3 pl-4 pr-12 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all"
        />
        <button 
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 transition-all"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </form>

      <div className="flex-1 overflow-y-auto space-y-6 pr-2 custom-scrollbar">
        {result ? (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
             <div className="space-y-4">
               <div className="flex gap-4">
                  <div className="w-1 h-auto bg-blue-500/30 rounded-full"></div>
                  <div className="flex-1">
                     <p className="text-sm text-slate-200 leading-relaxed font-medium">{result.answer}</p>
                  </div>
               </div>

               {result.recommendation && (
                 <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                    <p className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                       <CheckCircle2 className="w-3.5 h-3.5" /> Recommendation
                    </p>
                    <p className="text-xs text-emerald-100/80 leading-relaxed">{result.recommendation}</p>
                 </div>
               )}
             </div>

             {result.citations && result.citations.length > 0 && (
               <div className="space-y-3">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                     <Quote className="w-3 h-3" /> Grounded Citations
                  </p>
                  <div className="flex flex-wrap gap-2">
                     {result.citations.map((cite: any, i: number) => (
                       <span key={i} className="px-2 py-1 rounded bg-slate-900 border border-slate-800 text-[10px] text-slate-400 font-medium whitespace-nowrap">
                          {cite.title || cite}
                       </span>
                     ))}
                  </div>
               </div>
             )}
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-30 space-y-4">
             <HelpCircle className="w-12 h-12 text-slate-600" />
             <div className="space-y-1">
               <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Awaiting Inquiry</p>
               <p className="text-xs text-slate-600 max-w-[200px]">Query frameworks like NIST CSF, ISO 27001, or internal AI safety policies.</p>
             </div>
          </div>
        )}
      </div>
    </div>
  );
}
