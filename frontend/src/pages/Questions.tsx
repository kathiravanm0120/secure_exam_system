import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { questionsApi } from '../api/questions';
import { investigationApi } from '../api/investigation';
import { Question } from '../types';
import { Search, Plus, Eye, History, Shield, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Questions: React.FC = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [search, setSearch] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedLifecycle, setSelectedLifecycle] = useState<any | null>(null);

  const fetchQuestions = async () => {
    setIsLoading(true);
    try {
      const res = await questionsApi.getMyQuestions();
      setQuestions(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);

  const handleViewLifecycle = async (qid: number) => {
    try {
      const res = await investigationApi.getQuestionLifecycle(qid);
      setSelectedLifecycle(res);
    } catch (err: any) {
      alert(err.message || 'Failed to fetch question lifecycle');
    }
  };

  const filtered = questions.filter((q) => {
    const matchesSearch =
      q.content.toLowerCase().includes(search.toLowerCase()) ||
      q.topic.toLowerCase().includes(search.toLowerCase()) ||
      q.subject.toLowerCase().includes(search.toLowerCase());
    const matchesSubject = subjectFilter === 'ALL' || q.subject === subjectFilter;
    return matchesSearch && matchesSubject;
  });

  return (
    <AppShell title="Question Bank & Custody" subtitle="Encrypted question pool & complete visual lifecycle timeline">
      <div className="space-y-5">
        {/* Header Toolbar */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-4 border border-slate-200 rounded-2xl shadow-sm">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <div className="relative flex-1 sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search topics, questions..."
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />
            </div>

            <select
              value={subjectFilter}
              onChange={(e) => setSubjectFilter(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700"
            >
              <option value="ALL">All Subjects</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Physics">Physics</option>
            </select>
          </div>

          <Link
            to="/questions/create"
            className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-xs transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Create Question</span>
          </Link>
        </div>

        {/* Question Table */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-400 font-bold uppercase text-[11px] tracking-wider">
                  <th className="py-3 px-4 text-left">ID</th>
                  <th className="py-3 px-4 text-left">Subject / Topic</th>
                  <th className="py-3 px-4 text-left">Difficulty</th>
                  <th className="py-3 px-4 text-left">Status</th>
                  <th className="py-3 px-4 text-left">Integrity Hash</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {isLoading ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-slate-400 font-medium">
                      Loading encrypted question pool...
                    </td>
                  </tr>
                ) : filtered.length > 0 ? (
                  filtered.map((q) => (
                    <tr key={q.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900">Q{q.id}</td>
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-900">{q.subject}</div>
                        <div className="text-[11px] text-slate-500 font-medium">{q.topic}</div>
                      </td>
                      <td className="py-3 px-4 font-semibold text-slate-700">{q.difficulty}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                            q.status === 'APPROVED'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : q.status === 'REJECTED'
                              ? 'bg-red-50 text-red-700 border border-red-200'
                              : 'bg-amber-50 text-amber-700 border border-amber-200'
                          }`}
                        >
                          {q.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px] text-indigo-600">
                        {q.content_hash.slice(0, 16)}…
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleViewLifecycle(q.id)}
                          className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-lg text-[11px] transition-colors inline-flex items-center gap-1"
                        >
                          <History className="w-3.5 h-3.5" />
                          <span>Timeline</span>
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-slate-400 font-medium">
                      No questions found matching criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Visual Lifecycle Timeline Modal */}
        {selectedLifecycle && (
          <div className="fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-white border border-slate-200 rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
              <div className="p-5 border-b border-slate-200 flex justify-between items-center bg-slate-50">
                <div>
                  <h3 className="font-extrabold text-base text-slate-900">
                    Question Chain of Custody (Q{selectedLifecycle.question_id})
                  </h3>
                  <p className="text-xs text-slate-500 font-medium mt-0.5">
                    Stage-by-stage audit events and cryptographic hash references
                  </p>
                </div>
                <button
                  onClick={() => setSelectedLifecycle(null)}
                  className="px-3 py-1 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-lg text-xs font-bold"
                >
                  Close
                </button>
              </div>

              <div className="p-6 overflow-y-auto space-y-4">
                <div className="relative pl-6 border-l-2 border-slate-200 space-y-5">
                  {selectedLifecycle.timeline.map((event: any, idx: number) => (
                    <div key={idx} className="relative bg-slate-50 border border-slate-200 rounded-xl p-3.5">
                      <div className="absolute -left-[31px] top-3.5 w-3 h-3 rounded-full bg-blue-600 border-2 border-white" />
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-bold text-xs text-slate-900">{event.stage}</span>
                        <span className="text-[10px] text-slate-400 font-semibold">
                          {event.timestamp ? new Date(event.timestamp).toLocaleString() : 'N/A'}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-600">
                        Actor: <strong className="text-slate-800">{event.actor}</strong> ({event.actor_role}) · Source:{' '}
                        <i>{event.source}</i>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-1">{event.details}</p>
                      <div className="mt-2 text-[10px] font-mono text-indigo-600">Ref: {event.blockchain_ref}</div>
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
