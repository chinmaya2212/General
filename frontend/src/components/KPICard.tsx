import React from 'react';
import { LucideIcon, TrendingUp } from 'lucide-react';

interface KPICardProps {
  name: string;
  value: string | number;
  trend?: string;
  icon: LucideIcon;
  color: string;
}

export default function KPICard({ name, value, trend, icon: Icon, color }: KPICardProps) {
  return (
    <div className="glass p-6 rounded-2xl border border-slate-700/50 transition-all hover:scale-[1.02] active:scale-[0.98]">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-xl bg-slate-800/50 ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
        {trend && trend !== '0' && (
          <div className={`flex items-center gap-1 text-xs font-medium ${trend.startsWith('+') ? 'text-rose-400' : 'text-emerald-400'}`}>
            <TrendingUp className={`w-3 h-3 ${trend.startsWith('-') ? 'rotate-180' : ''}`} />
            {trend}
          </div>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-sm font-medium text-slate-400">{name}</p>
        <p className="text-3xl font-bold text-white tracking-tight">{value}</p>
      </div>
    </div>
  );
}
