"use client";

import { useState, useEffect } from 'react';
import { Search, Radar, Loader2, Info } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { Exposure } from '@/lib/types';
import ExposureList from '@/components/exposures/ExposureList';
import ExposureDetail from '@/components/exposures/ExposureDetail';

export default function ExposuresPage() {
  const [exposures, setExposures] = useState<Exposure[]>([]);
  const [filteredExposures, setFilteredExposures] = useState<Exposure[]>([]);
  const [selectedExposure, setSelectedExposure] = useState<Exposure | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadExposures() {
      try {
        setLoading(true);
        const data = await apiClient.getTopExposures(50);
        setExposures(data);
        setFilteredExposures(data);
        if (data.length > 0) setSelectedExposure(data[0]);
      } catch (error) {
        console.error('Failed to load exposures:', error);
      } finally {
        setLoading(false);
      }
    }
    loadExposures();
  }, []);

  useEffect(() => {
    let result = exposures;
    if (search) {
      result = result.filter(e => e.asset_name.toLowerCase().includes(search.toLowerCase()));
    }
    setFilteredExposures(result);
  }, [search, exposures]);

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight text-white glow-text">Exposure Management</h2>
          <p className="text-slate-400">Attack path analysis and predictive risk prioritization for critical assets.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text"
              placeholder="Filter assets..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-900/50 border border-slate-700/50 rounded-xl py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all w-64"
            />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 glass rounded-3xl flex items-center justify-center">
           <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
        </div>
      ) : (
        <div className="flex-1 flex gap-8 min-h-0">
          <div className="w-80 flex flex-col min-h-0">
            <div className="px-1 mb-2">
               <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">Ranked Priority</span>
            </div>
            <ExposureList 
              exposures={filteredExposures} 
              selectedId={selectedExposure?.asset_id || null} 
              onSelect={setSelectedExposure} 
            />
          </div>
          
          <div className="flex-1 min-w-0 min-h-0">
            {selectedExposure ? (
              <ExposureDetail exposure={selectedExposure} />
            ) : (
              <div className="h-full glass rounded-3xl border-dashed flex flex-col items-center justify-center text-center p-12 opacity-30">
                 <Radar className="w-12 h-12 mb-4" />
                 <p className="text-lg font-medium">Select an asset to analyze attack paths and exposure factors.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
