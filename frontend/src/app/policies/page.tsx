"use client";

import { useState } from 'react';
import { Search, Database, ShieldCheck, FileText, Info } from 'lucide-react';
import PolicyAdvisor from '@/components/policies/PolicyAdvisor';

const MOCK_POLICIES = [
  { id: 'pol-01', title: 'Generative AI Usage Policy', category: 'AI Governance', status: 'Active', framework: 'ISO 42001' },
  { id: 'pol-02', title: 'Data Encryption Standard', category: 'Technical Control', status: 'Active', framework: 'NIST CSF' },
  { id: 'pol-03', title: 'Access Control Guideline', category: 'Operations', status: 'Draft', framework: 'ISO 27001' },
  { id: 'pol-04', title: 'Incident Response Plan', category: 'Continuity', status: 'Review', framework: 'NIST 800-61' },
  { id: 'pol-05', title: 'Vendor Security Assessment', category: 'Supply Chain', status: 'Active', framework: 'SOC2 Type II' },
];

export default function PoliciesPage() {
  const [search, setSearch] = useState('');
  
  const filteredPolicies = MOCK_POLICIES.filter(p => 
    p.title.toLowerCase().includes(search.toLowerCase()) || 
    p.framework.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight text-white glow-text">Policies & Governance</h2>
          <p className="text-slate-400">Manage compliance frameworks, internal standards, and AI safety guardrails.</p>
        </div>
      </div>

      <div className="flex-1 flex gap-8 min-h-0">
        <div className="flex-1 flex flex-col space-y-6 min-h-0">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text"
              placeholder="Search standards or frameworks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all"
            />
          </div>

          <div className="flex-1 glass rounded-2xl border border-slate-700/50 overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-slate-700/30 flex items-center justify-between">
               <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                 <Database className="w-4 h-4" /> Governance Repository
               </h3>
               <span className="text-[10px] text-slate-500">{filteredPolicies.length} items identified</span>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
               {filteredPolicies.map((policy) => (
                 <div key={policy.id} className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/50 hover:border-slate-700 transition-all group flex items-center justify-between">
                    <div className="flex items-center gap-4">
                       <div className="p-2 rounded-lg bg-slate-800 flex items-center justify-center">
                          <FileText className="w-4 h-4 text-slate-400 group-hover:text-blue-400 transition-all" />
                       </div>
                       <div>
                          <p className="text-sm font-medium text-slate-200">{policy.title}</p>
                          <div className="flex items-center gap-3 mt-1">
                             <span className="text-[10px] text-slate-500">{policy.category}</span>
                             <span className="w-1 h-1 rounded-full bg-slate-700"></span>
                             <span className="text-[10px] text-blue-500/70 font-mono">{policy.framework}</span>
                          </div>
                       </div>
                    </div>
                    <div className="text-right">
                       <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-tighter ${
                         policy.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-slate-800 text-slate-500'
                       }`}>{policy.status}</span>
                    </div>
                 </div>
               ))}
            </div>
          </div>
        </div>

        <div className="w-96 shrink-0">
          <PolicyAdvisor />
        </div>
      </div>
    </div>
  );
}
