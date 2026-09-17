import React, { useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { examsApi } from '../api/exams';
import { identityApi } from '../api/identity';
import { PaperValidationReport } from '../types';
import { Award, ShieldCheck, CheckCircle2, AlertTriangle, Plus, ShieldAlert } from 'lucide-react';

export const Exams: React.FC = () => {
  const [examId, setExamId] = useState('2');
  const [validationReport, setValidationReport] = useState<PaperValidationReport | null>(null);
  const [releaseStatus, setReleaseStatus] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  // New Exam Form State
  const [name, setName] = useState('Computer Science Advanced Exam');
  const [subject, setSubject] = useState('Computer Science');
  const [topic, setTopic] = useState('Algorithms');
  const [difficulty, setDifficulty] = useState<'EASY' | 'MEDIUM' | 'HARD'>('MEDIUM');
  const [count, setCount] = useState(2);

  const handleValidate = async () => {
    setIsLoading(true);
    setMsg(null);
    try {
      const report = await examsApi.validatePaper(Number(examId));
      setValidationReport(report);
    } catch (err: any) {
      setMsg(err.message || 'Validation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApproveRelease = async () => {
    setIsLoading(true);
    try {
      await examsApi.approveRelease(Number(examId));
      setMsg('Officer release approval recorded on audit log!');
      const status = await examsApi.getReleaseStatus(Number(examId));
      setReleaseStatus(status);
    } catch (err: any) {
      setMsg(err.message || 'Release approval failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReleaseExam = async () => {
    setIsLoading(true);
    try {
      const res = await examsApi.release(Number(examId));
      setReleaseStatus(res);
      setMsg('Exam status updated to RELEASED!');
    } catch (err: any) {
      setMsg(err.message || 'Release failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateExam = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const starts_at = new Date(Date.now() - 5 * 60000).toISOString();
      const ends_at = new Date(Date.now() + 180 * 60000).toISOString();
      const res = await examsApi.create({
        name,
        subject,
        starts_at,
        ends_at,
        rules: [{ topic, difficulty, count: Number(count) }],
      });

      // Assign centre 1 to exam
      await identityApi.assignCentreToExam(res.id, 1);
      setMsg(`Exam #${res.id} created with blueprint rule topic='${topic}' count=${count}!`);
      setExamId(String(res.id));
    } catch (err: any) {
      setMsg(err.message || 'Exam creation failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppShell title="Exam Management & Release Controls" subtitle="Pre-Exam AI Validation, Dual-Officer Release, and Blueprint Rules">
      <div className="space-y-6">
        {msg && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-2xl text-xs font-semibold text-blue-800 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{msg}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Create Scheduled Exam Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Plus className="w-4 h-4 text-blue-600" />
              <span>Create Scheduled Exam & Blueprint</span>
            </h3>

            <form onSubmit={handleCreateExam} className="space-y-3 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Exam Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Subject</label>
                  <input
                    type="text"
                    required
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Blueprint Topic</label>
                  <input
                    type="text"
                    required
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value as any)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 font-semibold text-slate-900"
                  >
                    <option value="EASY">EASY</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HARD">HARD</option>
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Question Count</label>
                  <input
                    type="number"
                    required
                    min={1}
                    max={50}
                    value={count}
                    onChange={(e) => setCount(Number(e.target.value))}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-slate-900 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl text-xs shadow-md shadow-blue-500/20 transition-all disabled:opacity-50"
              >
                Create Exam & Blueprint
              </button>
            </form>
          </div>

          {/* Validation & Dual Officer Release Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Pre-Exam Validation & Dual-Officer Release</span>
            </h3>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Target Exam ID</label>
                <input
                  type="number"
                  value={examId}
                  onChange={(e) => setExamId(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-blue-500 font-bold"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <button
                  onClick={handleValidate}
                  disabled={isLoading}
                  className="px-3 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition-colors shadow-sm"
                >
                  Run Validation
                </button>
                <button
                  onClick={handleApproveRelease}
                  disabled={isLoading}
                  className="px-3 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition-colors shadow-sm"
                >
                  Officer Approve
                </button>
                <button
                  onClick={handleReleaseExam}
                  disabled={isLoading}
                  className="px-3 py-2.5 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl text-xs transition-colors shadow-sm"
                >
                  Release Exam
                </button>
              </div>
            </div>

            {/* Validation Report Display */}
            {validationReport && (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="font-extrabold text-slate-900">Validation Report:</span>
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      validationReport.status === 'PASS'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : validationReport.status === 'BLOCKED'
                        ? 'bg-red-50 text-red-700 border border-red-200'
                        : 'bg-amber-50 text-amber-700 border border-amber-200'
                    }`}
                  >
                    STATUS: {validationReport.status}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-medium text-slate-600 pt-1">
                  <div>Syllabus: <b>{validationReport.syllabus_coverage}</b></div>
                  <div>Difficulty: <b>{validationReport.difficulty_balance}</b></div>
                  <div>Duplicates: <b>{validationReport.duplicate_detection}</b></div>
                  <div>Approval: <b>{validationReport.approval_status}</b></div>
                </div>
                <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-200">
                  {validationReport.details.map((d, i) => (
                    <div key={i}>• {d}</div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
};
