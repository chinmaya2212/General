"use client";

import { useState, useEffect } from 'react';
import { Search, Filter, Loader2, Info } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Incident } from '@/lib/types';
import IncidentList from '@/components/incidents/IncidentList';
import IncidentDetail from '@/components/incidents/IncidentDetail';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [filteredIncidents, setFilteredIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadIncidents() {
      try {
        setLoading(true);
        const data = await apiClient.getIncidents();
        setIncidents(data);
        setFilteredIncidents(data);
        if (data.length > 0) setSelectedIncident(data[0]);
      } catch (error) {
        console.error('Failed to load incidents:', error);
      } finally {
        setLoading(false);
      }
    }
    loadIncidents();
  }, []);

  useEffect(() => {
    let result = incidents;
    if (search) {
      result = result.filter(i => i.name.toLowerCase().includes(search.toLowerCase()));
    }
    setFilteredIncidents(result);
  }, [search, incidents]);

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight text-white glow-text">Incident Investigations</h2>
          <p className="text-slate-400">Contextual tracing and narrative-building for high-impact security events.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text"
              placeholder="Search incidents..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-900/50 border border-slate-700/50 rounded-xl py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:ring-1 focus:ring-purple-500/50 transition-all w-64"
            />
          </div>
          <button className="p-2 rounded-xl bg-slate-900/50 border border-slate-700/50 text-slate-400 hover:text-white transition-all">
             <Filter className="w-4 h-4" />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 glass rounded-3xl flex items-center justify-center">
           <Loader2 className="w-10 h-10 text-purple-500 animate-spin" />
        </div>
      ) : (
        <div className="flex-1 flex gap-8 min-h-0">
          <div className="w-80 flex flex-col min-h-0">
            <IncidentList 
              incidents={filteredIncidents} 
              selectedId={selectedIncident?.id || null} 
              onSelect={setSelectedIncident} 
            />
          </div>
          
          <div className="flex-1 min-w-0 min-h-0">
            {selectedIncident ? (
              <IncidentDetail incident={selectedIncident} />
            ) : (
              <div className="h-full glass rounded-3xl border-dashed flex flex-col items-center justify-center text-center p-12 opacity-30">
                 <Info className="w-12 h-12 mb-4" />
                 <p className="text-lg font-medium">Select an incident to view investigation details.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
