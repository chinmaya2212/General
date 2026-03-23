"use client";

import { fetchWithAuth } from './auth';
import { Alert, Incident, KPI, Exposure, CopilotMessage } from './types';

const API_BASE = 'http://localhost:8000/api/v1';

export const apiClient = {
  // KPIs
  getKPISummary: async (): Promise<KPI> => {
    const res = await fetchWithAuth(`${API_BASE}/kpis/summary`);
    return res.json();
  },

  // Alerts
  getAlerts: async (limit: number = 50): Promise<Alert[]> => {
    const res = await fetchWithAuth(`${API_BASE}/alerts?limit=${limit}`);
    return res.json();
  },

  // Incidents
  getIncidents: async (limit: number = 50): Promise<Incident[]> => {
    const res = await fetchWithAuth(`${API_BASE}/incidents?limit=${limit}`);
    return res.json();
  },

  // Exposures
  getTopExposures: async (limit: number = 10): Promise<Exposure[]> => {
    const res = await fetchWithAuth(`${API_BASE}/exposures/top?limit=${limit}`);
    return res.json();
  },

  // Copilot
  chat: async (message: string, mode: string = 'soc', sessionId?: string): Promise<any> => {
    const res = await fetchWithAuth(`${API_BASE}/chat/copilot`, {
      method: 'POST',
      body: JSON.stringify({ message, mode, session_id: sessionId }),
    });
    return res.json();
  },

  // Ingestion (Admin only)
  ingestData: async (source: string, file?: File): Promise<any> => {
    // Note: Multipart/form-data handling omitted for simplicity in MVP
    const res = await fetchWithAuth(`${API_BASE}/ingest/${source}`, {
      method: 'POST',
    });
    return res.json();
  },

  // Agents
  runTriage: async (alertId: string): Promise<any> => {
    const res = await fetchWithAuth(`${API_BASE}/agents/triage`, {
      method: 'POST',
      body: JSON.stringify({ alert_id: alertId }),
    });
    return res.json();
  },

  // Investigation
  runInvestigation: async (targetId: string): Promise<any> => {
    const res = await fetchWithAuth(`${API_BASE}/agents/investigate`, {
      method: 'POST',
      body: JSON.stringify({ target_id: targetId }),
    });
    return res.json();
  },

  // Policy Advisor
  askPolicyAdvisor: async (query: string): Promise<any> => {
    const res = await fetchWithAuth(`${API_BASE}/agents/policy-advisor`, {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
    return res.json();
  },

  // Graph
  getEntity: async (id: string): Promise<any> => {
    const res = await fetchWithAuth(`${API_BASE}/graph/entities/${id}`);
    return res.json();
  },

  getNeighbors: async (id: string): Promise<any> => {
    const res = await fetchWithAuth(`${API_BASE}/graph/entities/${id}/neighbors`);
    return res.json();
  },

  // System & Admin
  getSystemStatus: async (): Promise<any> => {
    const res = await fetchWithAuth(`${API_BASE}/system/status`);
    return res.json();
  },

  runAdminAction: async (action: string): Promise<any> => {
    const res = await fetchWithAuth(`${API_BASE}/system/admin/run`, {
      method: 'POST',
      body: JSON.stringify({ action }),
    });
    return res.json();
  }
};





