"use client";

import React from 'react';
import { 
  ArrowUpRight, 
  Server, 
  Bug, 
  ShieldCheck, 
  FileLock2, 
  User,
  ExternalLink
} from 'lucide-react';

interface Relationship {
  id: string;
  name: string;
  type: string;
  relation: string;
}

interface RelationshipListProps {
  label: string;
  items: Relationship[];
  onPivot: (id: string) => void;
}

const getIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'asset': return Server;
    case 'vulnerability': return Bug;
    case 'policy': return ShieldCheck;
    case 'incident': return FileLock2;
    case 'identity': return User;
    default: return ExternalLink;
  }
};

export default function RelationshipList({ label, items, onPivot }: RelationshipListProps) {
  if (items.length === 0) return null;

  return (
    <div className="space-y-3">
       <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{label}</p>
       <div className="grid grid-cols-1 gap-2">
          {items.map((item) => {
            const Icon = getIcon(item.type);
            return (
              <button
                key={item.id}
                onClick={() => onPivot(item.id)}
                className="glass p-3 rounded-xl border border-slate-800/50 hover:border-slate-700 transition-all flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                   <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-700">
                      <Icon className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-400" />
                   </div>
                   <div className="text-left">
                      <p className="text-xs font-semibold text-slate-200">{item.name}</p>
                      <p className="text-[10px] text-slate-500">{item.relation}</p>
                   </div>
                </div>
                <ArrowUpRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-blue-500 transition-all opacity-0 group-hover:opacity-100 translate-x-[-4px] group-hover:translate-x-0" />
              </button>
            );
          })}
       </div>
    </div>
  );
}
