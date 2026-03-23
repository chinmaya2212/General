export type UserRole = 'admin' | 'analyst' | 'executive';

export interface User {
  id: string;
  email: string;
  role: UserRole;
}

export interface Alert {
  id: string;
  name: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'open' | 'triaged' | 'closed';
  source: string;
  created_at: string;
  description?: string;
}

export interface Incident {
  id: string;
  name: string;
  status: 'new' | 'open' | 'investigating' | 'resolved' | 'closed';
  severity: string;
  summary?: string;
  created_at: string;
}

export interface KPI {
  alerts: {
    open_count: number;
    critical_count: number;
  };
  incidents: {
    active_count: number;
    mttr_hours_avg: number;
  };
  exposure: {
    avg_top_score: number;
    highly_exposed_assets: number;
  };
  governance: {
    total_policies: number;
    total_controls: number;
    coverage_percent: number;
  };
  executive_summary: string;
}

export interface Exposure {
  asset_id: string;
  asset_name: string;
  base_score: number;
  metrics: {
    criticality_factor: number;
    max_cvss: number;
    is_reachable: boolean;
    privilege_risk: boolean;
  };
  rationale: string[];
  remediation_plan: string[];
}

export interface CopilotMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: string[];
}
