import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { securityApi } from '../api/security';
import { SecurityAlert } from '../types';
import { ShieldAlert, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

export const SecurityCenter: React.FC = () => {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const res = await securityApi.getAlerts();
      setAlerts(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleResolve = async (id: number) => {
    try {
      await securityApi.resolveAlert(id);
      alert(`Alert #${id} marked as RESOLVED`);
      fetchAlerts();
    } catch (err: any) {
      alert(err.message || 'Failed to resolve alert');
    }
  };

  const filtered = alerts.filter((a) => filterSeverity === 'ALL' || a.severity === filterSeverity);

  return (
    <AppShell title="Security Operations Center" subtitle="Behavior risk engine alerts & suspicious activity monitoring">
      <div className="space-y-6">
        {/* Severity Toolbar */}
        <div className="flex justify-between items-center bg-white p-4 border border-slate-200 rounded-2xl shadow-sm">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-500" />
            <h3 className="text-xs font-bold text-slate-900">Security Risk Stream</h3>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-500">Filter Severity:</span>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-800"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>
        </div>

        {/* Alerts Table */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase text-[11px] tracking-wider">
                  <th className="py-3 px-4 text-left">Alert ID</th>
                  <th className="py-3 px-4 text-left">Severity</th>
                  <th className="py-3 px-4 text-left">Risk Score</th>
                  <th className="py-3 px-4 text-left">Candidate / Session</th>
                  <th className="py-3 px-4 text-left">Detected Reasons</th>
                  <th className="py-3 px-4 text-left">Status</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {isLoading ? (
                  <tr>
                    <td colSpan={7} className="text-center py-8 text-slate-400 font-medium">
                      Loading security alerts...
                    </td>
                  </tr>
                ) : filtered.length > 0 ? (
                  filtered.map((alert) => (
                    <tr key={alert.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-bold text-slate-900">#{alert.id}</td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            alert.severity === 'CRITICAL' || alert.severity === 'HIGH'
                              ? 'bg-red-50 text-red-700 border border-red-200'
                              : alert.severity === 'MEDIUM'
                              ? 'bg-amber-50 text-amber-700 border border-amber-200'
                              : 'bg-blue-50 text-blue-700 border border-blue-200'
                          }`}
                        >
                          {alert.severity}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-black text-slate-900">{alert.risk_score} / 100</td>
                      <td className="py-3.5 px-4 text-slate-600 font-medium">
                        Candidate #{alert.candidate_id ?? 'N/A'} · Session #{alert.session_id ?? 'N/A'}
                      </td>
                      <td className="py-3.5 px-4 text-slate-600 font-medium max-w-xs">
                        {alert.reasons.join(', ')}
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            alert.status === 'OPEN'
                              ? 'bg-red-50 text-red-700 border border-red-200'
                              : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          }`}
                        >
                          {alert.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        {alert.status === 'OPEN' ? (
                          <button
                            onClick={() => handleResolve(alert.id)}
                            className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-[11px] transition-colors shadow-sm"
                          >
                            Resolve
                          </button>
                        ) : (
                          <span className="text-slate-400 font-medium">—</span>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="text-center py-8 text-slate-400 font-medium">
                      No security alerts found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  );
};
