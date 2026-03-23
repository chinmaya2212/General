import React from 'react';
import { Shield, Layout, Database, Radar } from 'lucide-react';

export type CopilotMode = 'ciso' | 'soc' | 'policy' | 'exposure';

interface ModeSelectorProps {
  currentMode: CopilotMode;
  onModeChange: (mode: CopilotMode) => void;
}

const modes = [
  { id: 'soc', name: 'SOC Operations', description: 'Investigate alerts & threats', icon: Shield, color: 'text-blue-500' },
  { id: 'ciso', name: 'Executive Strategy', description: 'Risk & posture overview', icon: Layout, color: 'text-purple-500' },
  { id: 'policy', name: 'Policy Advisor', description: 'Compliance & governance', icon: Database, color: 'text-emerald-500' },
  { id: 'exposure', name: 'Exposure Analyst', description: 'Attack paths & vulns', icon: Radar, color: 'text-amber-500' },
];

export default function ChatModeSelector({ currentMode, onModeChange }: ModeSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {modes.map((mode) => {
        const Icon = mode.icon;
        const isActive = currentMode === mode.id;
        return (
          <button
            key={mode.id}
            onClick={() => onModeChange(mode.id as CopilotMode)}
            className={`glass p-4 rounded-xl border text-left transition-all hover:scale-[1.02] active:scale-[0.98] ${
              isActive ? 'border-blue-500/50 bg-blue-500/5 ring-1 ring-blue-500/30' : 'border-slate-800'
            }`}
          >
            <div className={`p-2 rounded-lg bg-slate-800/50 w-fit mb-3 ${mode.color}`}>
              <Icon className="w-5 h-5" />
            </div>
            <h4 className="font-semibold text-white text-sm">{mode.name}</h4>
            <p className="text-xs text-slate-500 mt-1">{mode.description}</p>
          </button>
        );
      })}
    </div>
  );
}
