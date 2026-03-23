"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  ShieldAlert, 
  Search, 
  LayoutDashboard, 
  MessageSquare, 
  FileLock2, 
  Database, 
  Settings,
  Radar
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Alerts', href: '/alerts', icon: ShieldAlert },
  { name: 'Incidents', href: '/incidents', icon: FileLock2 },
  { name: 'Exposure', href: '/exposures', icon: Radar },
  { name: 'Copilot', href: '/copilot', icon: MessageSquare },
  { name: 'Policies', href: '/policies', icon: Database },
  { name: 'Knowledge', href: '/knowledge', icon: Search },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 glass border-r flex flex-col z-50">
      <div className="p-6 flex items-center gap-2">
        <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center">
          <ShieldAlert className="w-5 h-5 text-white" />
        </div>
        <span className="font-bold text-xl tracking-tight">AI<span className="text-blue-500">Sec</span></span>
      </div>

      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link 
              key={item.name} 
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive 
                ? 'text-white bg-blue-600/20 border-l-2 border-blue-500 shadow-lg' 
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-blue-400' : ''}`} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 mt-auto">
        <Link 
          href="/settings"
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
        >
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </Link>
      </div>
    </aside>
  );
}
