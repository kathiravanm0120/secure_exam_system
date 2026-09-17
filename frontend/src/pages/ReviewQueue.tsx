import React, { useEffect, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { questionsApi } from '../api/questions';
import { Question } from '../types';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

export const ReviewQueue: React.FC = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [rejectReason, setRejectReason] = useState<Record<number, string>>({});
  const [isLoading, setIsLoading] = useState(true);

  const fetchAssigned = async () => {
    setIsLoading(true);
    try {
      const res = await questionsApi.getMyQuestions();
      setQuestions(res.filter((q) => q.status === 'IN_REVIEW' || q.status === 'SUBMITTED'));
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAssigned();
  }, []);

  const handleReview = async (id: number, decision: 'APPROVE' | 'REJECT') => {
    const comments = decision === 'REJECT' ? rejectReason[id] || 'Rejected during review' : 'Approved during review';
    if (decision === 'REJECT' && !rejectReason[id]?.trim()) {
      alert('Please provide a reason for rejecting the question.');
      return;
    }

    try {
      await questionsApi.review(id, { decision, comments });
      alert(`Question Q${id} ${decision.toLowerCase()}d!`);
      fetchAssigned();
    } catch (err: any) {
      alert(err.message || 'Review action failed');
    }
  };

  return (
    <AppShell title="Reviewer Workspace" subtitle="Independently review assigned questions without full paper access">
      <div className="space-y-4 max-w-4xl">
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex justify-between items-center">
          <span className="text-xs font-bold text-slate-700">Assigned Pending Reviews</span>
          <span className="px-2.5 py-1 bg-blue-50 text-blue-700 border border-blue-200 rounded-full text-xs font-extrabold">
            {questions.length} Pending
          </span>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-slate-400 text-xs font-medium">Loading review queue...</div>
        ) : questions.length > 0 ? (
          <div className="space-y-4">
            {questions.map((q) => (
              <div key={q.id} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-xs font-extrabold text-slate-900">Question Q{q.id}</span>
                    <div className="text-[11px] text-slate-500 font-medium">
                      {q.subject} · {q.topic} ({q.difficulty})
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                    {q.status}
                  </span>
                </div>

                <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-xl text-xs text-slate-800 leading-relaxed">
                  {q.content}
                </div>

                <div className="text-[11px] font-mono text-indigo-600">Integrity Hash: {q.content_hash}</div>

                <div className="pt-2 flex flex-col sm:flex-row gap-3">
                  <input
                    type="text"
                    value={rejectReason[q.id] || ''}
                    onChange={(e) => setRejectReason({ ...rejectReason, [q.id]: e.target.value })}
                    placeholder="Comment / Reason (required if rejecting)..."
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-500"
                  />

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleReview(q.id, 'APPROVE')}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-xs transition-colors flex items-center gap-1.5 shadow-sm"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Approve</span>
                    </button>

                    <button
                      onClick={() => handleReview(q.id, 'REJECT')}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl text-xs transition-colors flex items-center gap-1.5 shadow-sm"
                    >
                      <XCircle className="w-4 h-4" />
                      <span>Reject</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center text-slate-400 text-xs font-medium">
            No questions are currently waiting for your review.
          </div>
        )}
      </div>
    </AppShell>
  );
};
