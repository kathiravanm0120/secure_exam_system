import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { dashboardApi } from '../api/dashboard';
import { DashboardSummary } from '../types';
import {
  FileText,
  ShieldAlert,
  Database,
  Lock,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const summary = await dashboardApi.getSummary();
      setData(summary);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard summary');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  return (
    <AppShell title="Security Operations Dashboard" subtitle="Real-time exam security telemetry & integrity monitoring">
      <div className="space-y-6">
        {/* Top Actions & Refresh */}
        <div className="flex justify-between items-center">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">System Key Metrics</h3>
          <button
            onClick={fetchSummary}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-2xl text-xs text-red-700 font-semibold">
            {error}
          </div>
        )}

        {/* 1. Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="flex justify-between items-start">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total Questions</span>
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-3xl font-black text-slate-900 mt-2">{data?.totals.questions ?? '—'}</div>
            <div className="text-xs text-emerald-600 font-bold mt-1">
              ✓ {data?.totals.approved_questions ?? 0} Approved Pool
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="flex justify-between items-start">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Active CBT Sessions</span>
              <Lock className="w-5 h-5 text-indigo-600" />
            </div>
            <div className="text-3xl font-black text-slate-900 mt-2">{data?.totals.active_sessions ?? '—'}</div>
            <div className="text-xs text-slate-500 font-medium mt-1">Device & Centre Bound</div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="flex justify-between items-start">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Security Alerts</span>
              <ShieldAlert className={`w-5 h-5 ${data?.totals.open_alerts ? 'text-red-500' : 'text-slate-400'}`} />
            </div>
            <div className="text-3xl font-black text-slate-900 mt-2">{data?.totals.open_alerts ?? '—'}</div>
            <div className={`text-xs font-bold mt-1 ${data?.totals.open_alerts ? 'text-red-600' : 'text-emerald-600'}`}>
              {data?.totals.open_alerts ? '⚠️ Requires Investigation' : '✓ No Open Alerts'}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <div className="flex justify-between items-start">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Blockchain Audit</span>
              <Database className="w-5 h-5 text-purple-600" />
            </div>
            <div className="text-3xl font-black text-slate-900 mt-2">
              {data?.chain.verification.valid ? 'VALID' : 'INVALID'}
            </div>
            <div className="text-xs text-slate-500 font-medium mt-1">
              {data?.chain.verification.blocks ?? 0} Immutable Blocks
            </div>
          </div>
        </div>

        {/* 2. Middle Grid: Exposure & Security Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Highest Exposure Table */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-sm font-bold text-slate-900">Highest Item Exposure</h4>
              <span className="text-[11px] text-slate-400 font-semibold">Top Exposed Items</span>
            </div>

            {data?.exposure_ranking && data.exposure_ranking.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-slate-100 text-slate-400 text-[11px] font-bold uppercase">
                      <th className="py-2.5 text-left">ID</th>
                      <th className="py-2.5 text-left">Topic</th>
                      <th className="py-2.5 text-left">Difficulty</th>
                      <th className="py-2.5 text-left">Exposure</th>
                      <th className="py-2.5 text-left">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {data.exposure_ranking.slice(0, 5).map((q) => (
                      <tr key={q.id} className="hover:bg-slate-50">
                        <td className="py-2.5 font-bold text-slate-900">Q{q.id}</td>
                        <td className="py-2.5 font-medium text-slate-600">{q.topic}</td>
                        <td className="py-2.5 font-medium text-slate-600">{q.difficulty}</td>
                        <td className="py-2.5 font-bold text-slate-900">{q.exposure_count}</td>
                        <td className="py-2.5">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              q.exposure_status === 'ACTIVE'
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : 'bg-amber-50 text-amber-700 border border-amber-200'
                            }`}
                          >
                            {q.exposure_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-xs text-slate-400 font-medium">
                No exposure metrics recorded yet.
              </div>
            )}
          </div>

          {/* Security Alerts */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-sm font-bold text-slate-900">Recent Security Alerts</h4>
              <span className="text-[11px] text-slate-400 font-semibold">Risk Engine Stream</span>
            </div>

            {data?.recent_alerts && data.recent_alerts.length > 0 ? (
              <div className="space-y-3">
                {data.recent_alerts.slice(0, 4).map((alert) => (
                  <div key={alert.id} className="p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-900">Alert #{alert.id}</span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          alert.severity === 'CRITICAL' || alert.severity === 'HIGH'
                            ? 'bg-red-50 text-red-700 border border-red-200'
                            : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}
                      >
                        {alert.severity} · Risk {alert.risk_score}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 font-medium leading-relaxed">
                      {alert.reasons.join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-xs text-slate-400 font-medium">
                No recent security alerts. System operating normally.
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
};
