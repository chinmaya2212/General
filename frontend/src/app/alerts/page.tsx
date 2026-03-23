"use client";

import { useState, useEffect } from 'react';
import { Search, Filter, Loader2, Info } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Alert } from '@/lib/types';
import AlertList from '@/components/alerts/AlertList';
import AlertDetail from '@/components/alerts/AlertDetail';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filteredAlerts, setFilteredAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');

  useEffect(() => {
    async function loadAlerts() {
      try {
        setLoading(true);
        const data = await apiClient.getAlerts();
        setAlerts(data);
        setFilteredAlerts(data);
        if (data.length > 0) setSelectedAlert(data[0]);
      } catch (error) {
        console.error('Failed to load alerts:', error);
      } finally {
        setLoading(false);
      }
    }
    loadAlerts();
  }, []);

  useEffect(() => {
    let result = alerts;
    if (search) {
      result = result.filter(a => a.name.toLowerCase().includes(search.toLowerCase()) || a.source.toLowerCase().includes(search.toLowerCase()));
    }
    if (severityFilter !== 'all') {
      result = result.filter(a => a.severity === severityFilter);
    }
    setFilteredAlerts(result);
  }, [search, severityFilter, alerts]);

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight text-white glow-text">Alert Triage Queue</h2>
          <p className="text-slate-400">Manage and prioritize security events across the enterprise.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text"
              placeholder="Search alerts..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-900/50 border border-slate-700/50 rounded-xl py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all w-64"
            />
          </div>
          <select 
             value={severityFilter}
             onChange={(e) => setSeverityFilter(e.target.value)}
             className="bg-slate-900/50 border border-slate-700/50 rounded-xl py-2 px-4 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500/50"
          >
             <option value="all">All Severities</option>
             <option value="critical">Critical Only</option>
             <option value="high">High +</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 glass rounded-3xl flex items-center justify-center">
           <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
        </div>
      ) : (
        <div className="flex-1 flex gap-8 min-h-0">
          <div className="w-80 flex flex-col min-h-0">
            <AlertList 
              alerts={filteredAlerts} 
              selectedId={selectedAlert?.id || null} 
              onSelect={setSelectedAlert} 
            />
          </div>
          
          <div className="flex-1 min-w-0 min-h-0">
            {selectedAlert ? (
              <AlertDetail alert={selectedAlert} />
            ) : (
              <div className="h-full glass rounded-3xl border-dashed flex flex-col items-center justify-center text-center p-12 opacity-30">
                 <Info className="w-12 h-12 mb-4" />
                 <p className="text-lg font-medium">Select an alert from the queue to begin triage.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
