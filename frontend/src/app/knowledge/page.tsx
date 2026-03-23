"use client";

import { useState, useEffect } from 'react';
import { Search, Loader2, Network, Info, Share2, Database, Box } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import RelationshipList from '@/components/knowledge/RelationshipList';

interface Entity {
  id: string;
  name: string;
  type: string;
  attributes: Record<string, any>;
}

export default function KnowledgePage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [entity, setEntity] = useState<Entity | null>(null);
  const [neighbors, setNeighbors] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  const loadEntity = async (id: string) => {
    setLoading(true);
    try {
      const [entityData, neighborData] = await Promise.all([
        apiClient.getEntity(id),
        apiClient.getNeighbors(id)
      ]);
      setEntity(entityData);
      setNeighbors(neighborData);
      setSelectedId(id);
    } catch (error) {
      console.error('Failed to load entity:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim()) {
      loadEntity(search.trim());
    }
  };

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-2">
          <h2 className="text-3xl font-bold tracking-tight text-white glow-text">Graph Explorer</h2>
          <p className="text-slate-400">Lightweight relationship traversal across security entities and knowledge nodes.</p>
        </div>
        
        <form onSubmit={handleSearch} className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text"
              placeholder="Enter Entity ID (e.g., Asset-01)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-slate-900/50 border border-slate-700/50 rounded-xl py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500/50 transition-all w-80"
            />
          </div>
          <button type="submit" className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all">
             Search Graph
          </button>
        </form>
      </div>

      <div className="flex-1 flex gap-8 min-h-0">
        <div className="flex-1 glass rounded-3xl border border-slate-700/50 flex flex-col overflow-hidden">
           {loading ? (
             <div className="flex-1 flex flex-col items-center justify-center gap-4">
                <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
                <p className="text-slate-500 text-sm font-medium">Traversing Graph Edges...</p>
             </div>
           ) : entity ? (
             <div className="flex-1 overflow-y-auto p-8 space-y-8 animate-in fade-in zoom-in-95 duration-500">
                <div className="flex items-start justify-between">
                   <div className="space-y-2">
                      <div className="flex items-center gap-2">
                         <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-widest">{entity.type}</span>
                         <span className="text-[10px] text-slate-500 font-mono">{entity.id}</span>
                      </div>
                      <h3 className="text-2xl font-bold text-white">{entity.name}</h3>
                   </div>
                   <div className="p-3 rounded-2xl bg-slate-900 border border-slate-800">
                      <Network className="w-8 h-8 text-blue-500 opacity-50" />
                   </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                   {Object.entries(entity.attributes || {}).map(([key, val]) => (
                     <div key={key} className="p-4 rounded-xl bg-slate-900/40 border border-slate-800/50">
                        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-1">{key.replace(/_/g, ' ')}</p>
                        <p className="text-xs text-slate-300 font-medium truncate">{String(val)}</p>
                     </div>
                   ))}
                </div>

                <div className="pt-8 border-t border-slate-800/50">
                   <h4 className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-6">
                      <Share2 className="w-4 h-4 text-blue-500" /> Adjacency Relationships
                   </h4>
                   
                   <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                      <RelationshipList 
                         label="Inbound Connections" 
                         items={neighbors.filter(n => n.direction === 'in')} 
                         onPivot={loadEntity} 
                      />
                      <RelationshipList 
                         label="Direct References" 
                         items={neighbors.filter(n => n.direction === 'out')} 
                         onPivot={loadEntity} 
                      />
                      <RelationshipList 
                         label="Environment Context" 
                         items={neighbors.filter(n => n.type === 'policy' || n.type === 'document')} 
                         onPivot={loadEntity} 
                      />
                   </div>
                </div>
             </div>
           ) : (
             <div className="flex-1 flex flex-col items-center justify-center text-center p-12 opacity-30 space-y-6">
                <div className="relative">
                   <Box className="w-16 h-16 text-slate-600" />
                   <div className="absolute inset-0 animate-ping opacity-20">
                      <Box className="w-16 h-16 text-blue-500" />
                   </div>
                </div>
                <div className="space-y-2">
                   <p className="text-xl font-bold text-white">Start Your Traversal</p>
                   <p className="text-sm text-slate-500 max-w-sm">Search for an asset, vulnerability, or incident ID to explore its relationships across the enterprise graph.</p>
                </div>
             </div>
           )}
        </div>

        <div className="w-64 glass rounded-3xl border border-slate-700/50 p-6 flex flex-col space-y-6">
           <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
              <Database className="w-3.5 h-3.5" /> Recent Traversed
           </h4>
           <div className="flex-1 text-center py-12 opacity-20 italic text-xs text-slate-500">
              No recent pivots.
           </div>
           <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-500/20">
              <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-2">Graph Insight</p>
              <p className="text-[10px] text-slate-400 leading-relaxed italic">The Knowledge Graph correlates evidence across silos to uncover hidden blast radii.</p>
           </div>
        </div>
      </div>
    </div>
  );
}
