import React, { useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { investigationApi } from '../api/investigation';
import { InvestigationResult } from '../types';
import { Search, History, ShieldAlert, CheckCircle2, User, FileText } from 'lucide-react';

export const Investigation: React.FC = () => {
  const [suspectedText, setSuspectedText] = useState('What is the time complexity of array lookup by index?');
  const [documentHash, setDocumentHash] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<InvestigationResult | null>(null);
  const [selectedTimeline, setSelectedTimeline] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const res = await investigationApi.analyzeLeak(suspectedText, undefined, documentHash || undefined);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Investigation analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenTimeline = async (qid: number) => {
    try {
      const res = await investigationApi.getQuestionLifecycle(qid);
      setSelectedTimeline(res);
    } catch (err: any) {
      alert(err.message || 'Failed to load question lifecycle');
    }
  };

  return (
    <AppShell title="Leak Investigation Workstation" subtitle="Cryptographic matching & automated leak origin tracing">
      <div className="space-y-6 max-w-4xl">
        {/* Search & Analysis Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Search className="w-4 h-4 text-blue-600" />
            <span>Suspected Document / Leaked Question Analysis</span>
          </h3>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs font-semibold">
              {error}
            </div>
          )}

          <form onSubmit={handleAnalyze} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold text-slate-700 mb-1">Suspected Leaked Text / Question Snippet</label>
              <textarea
                required
                rows={3}
                value={suspectedText}
                onChange={(e) => setSuspectedText(e.target.value)}
                placeholder="Paste extracted question snippet or leaked text..."
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-slate-900 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block font-bold text-slate-700 mb-1">Optional Exact SHA-256 Hash</label>
              <input
                type="text"
                value={documentHash}
                onChange={(e) => setDocumentHash(e.target.value)}
                placeholder="e.g. 5d41402abc4b2a76b9719d911017c592..."
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:border-blue-500 font-mono text-[11px]"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow-md shadow-blue-500/20 transition-all disabled:opacity-50"
            >
              {isLoading ? 'Analyzing Question Pool...' : 'Analyze & Trace Leak Origin'}
            </button>
          </form>
        </div>

        {/* Results Presentation */}
        {result && (
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900">Analysis Output</h3>

            {result.top_match ? (
              <div className="space-y-4">
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-extrabold text-red-900 text-sm">
                      ⚠️ Match Identified! Confidence: {(result.top_match.confidence * 100).toFixed(1)}%
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-600 text-white">
                      QUESTION Q{result.top_match.question_id}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs text-slate-800">
                    <div>
                      Subject: <strong>{result.top_match.subject}</strong> · Topic: <strong>{result.top_match.topic}</strong>
                    </div>
                    <div>
                      Difficulty: <strong>{result.top_match.difficulty}</strong> · Status: <strong>{result.top_match.status}</strong>
                    </div>
                    <div>
                      Creator: <strong>{result.top_match.created_by?.name || 'N/A'}</strong> ({result.top_match.created_by?.email})
                    </div>
                    <div>
                      Reviewer: <strong>{result.top_match.reviewed_by?.name || 'N/A'}</strong>
                    </div>
                  </div>

                  <div className="pt-2 text-[11px] text-slate-600">
                    Sessions Delivered: <b>{result.top_match.sessions_received_count}</b> · Security Events: <b>{result.top_match.security_events_count}</b> · Blockchain Events: <b>{result.top_match.blockchain_audit_events_count}</b>
                  </div>
                </div>

                <button
                  onClick={() => handleOpenTimeline(result.top_match!.question_id)}
                  className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-2.5 rounded-xl text-xs flex items-center justify-center gap-1.5"
                >
                  <History className="w-4 h-4" />
                  <span>Open Full Visual Chain of Custody Timeline</span>
                </button>
              </div>
            ) : (
              <div className="p-6 text-center text-slate-400 text-xs font-medium border border-slate-200 rounded-xl">
                No matching question found in the encrypted question pool for the suspected text.
              </div>
            )}
          </div>
        )}

        {/* Timeline Modal */}
        {selectedTimeline && (
          <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white border border-slate-200 rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
              <div className="p-5 border-b border-slate-200 flex justify-between items-center bg-slate-50">
                <div>
                  <h3 className="font-extrabold text-base text-slate-900">
                    Visual Lifecycle Timeline (Q{selectedTimeline.question_id})
                  </h3>
                  <p className="text-xs text-slate-500 font-medium">Chain of custody audit trail</p>
                </div>
                <button
                  onClick={() => setSelectedTimeline(null)}
                  className="px-3 py-1 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-lg text-xs font-bold"
                >
                  Close
                </button>
              </div>

              <div className="p-6 overflow-y-auto space-y-3">
                <div className="relative pl-6 border-l-2 border-slate-200 space-y-4">
                  {selectedTimeline.timeline.map((event: any, idx: number) => (
                    <div key={idx} className="relative bg-slate-50 border border-slate-200 rounded-xl p-3">
                      <div className="absolute -left-[31px] top-3 w-3 h-3 rounded-full bg-blue-600 border-2 border-white" />
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-bold text-xs text-slate-900">{event.stage}</span>
                        <span className="text-[10px] text-slate-400 font-semibold">
                          {event.timestamp ? new Date(event.timestamp).toLocaleString() : 'N/A'}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-600">
                        Actor: <b>{event.actor}</b> ({event.actor_role})
                      </div>
                      <p className="text-[11px] text-slate-500 mt-0.5">{event.details}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
};
