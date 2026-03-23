"use client";

import { useEffect, useState } from 'react';
import { ShieldAlert, FileLock2, Radar, Activity } from 'lucide-react';
import { apiClient } from '@/lib/api-client';
import { KPI, Alert, Exposure } from '@/lib/types';
import KPICard from '@/components/KPICard';
import DataTable from '@/components/DataTable';
import ExecutiveSummary from '@/components/ExecutiveSummary';
import LoadingState from '@/components/LoadingState';
import ErrorState from '@/components/ErrorState';
import { useAuth } from '@/context/AuthContext';

export default function Dashboard() {
  const [kpis, setKpis] = useState<KPI | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [exposures, setExposures] = useState<Exposure[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [kpiData, alertsData, exposuresData] = await Promise.all([
          apiClient.getKPISummary(),
          apiClient.getAlerts(5),
          apiClient.getTopExposures(5)
        ]);
        setKpis(kpiData);
        setAlerts(alertsData);
        setExposures(exposuresData);
      } catch (err) {
        setError("Failed to synchronize with security gateway.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState onRetry={() => window.location.reload()} />;

  return (
    <main className="space-y-8 animate-in fade-in duration-700">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-3xl font-bold tracking-tight text-white glow-text">CISO Command Center</h2>
          <p className="text-slate-400">Security posture and threat landscape overview.</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800">
           <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
           <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Real-time Feed Active</span>
        </div>
      </header>

      <div className="dashboard-grid">
        <KPICard 
          name="Active Alerts" 
          value={kpis?.alerts.open_count || 0} 
          trend={kpis?.alerts.critical_count ? `+${kpis.alerts.critical_count} critical` : "0"} 
          icon={ShieldAlert} 
          color="text-amber-500" 
        />
        <KPICard 
          name="Open Incidents" 
          value={kpis?.incidents.active_count || 0} 
          trend="0" 
          icon={FileLock2} 
          color="text-rose-500" 
        />
        <KPICard 
          name="Exposure Index" 
          value={kpis?.exposure.avg_top_score || 0} 
          trend={kpis?.exposure.highly_exposed_assets ? `+${kpis.exposure.highly_exposed_assets} assets` : "Stable"} 
          icon={Radar} 
          color="text-blue-500" 
        />
        <KPICard 
          name="Policy Coverage" 
          value={`${kpis?.governance.coverage_percent}%`} 
          icon={Activity} 
          color="text-emerald-500" 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <DataTable 
            title="Recent Critical Alerts"
            data={alerts}
            emptyMessage="No untriaged alerts detected."
            columns={[
              { header: 'Severity', render: (a) => (
                <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                  a.severity === 'critical' ? 'bg-rose-500/20 text-rose-500' : 'bg-slate-800 text-slate-400'
                }`}>{a.severity}</span>
              )},
              { header: 'Status', render: (a) => a.status },
              { header: 'Alert Detail', render: (a) => <span className="font-medium text-slate-200">{a.name}</span> },
              { header: 'Detected', render: (a) => new Date(a.created_at).toLocaleDateString() },
            ]}
          />

          <DataTable 
            title="Top Asset Exposures"
            data={exposures}
            emptyMessage="No high-risk exposures identified."
            columns={[
              { header: 'Risk Score', render: (e) => (
                <span className="font-bold text-blue-400">{e.base_score}</span>
              )},
              { header: 'Asset Name', render: (e) => <span className="font-medium text-slate-200">{e.asset_name}</span> },
              { header: 'Direct Exposure', render: (e) => (
                <span className={e.metrics.is_reachable ? 'text-amber-500' : 'text-emerald-500'}>
                  {e.metrics.is_reachable ? 'External' : 'Internal'}
                </span>
              )},
              { header: 'Remediation', render: (e) => (
                <span className="text-xs truncate max-w-[150px] inline-block">{e.remediation_plan[0] || 'N/A'}</span>
              )},
            ]}
          />
        </div>

        <div className="h-full">
          <ExecutiveSummary summary={kpis?.executive_summary || ""} />
        </div>
      </div>
    </main>
  );
}
