import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { questionsApi } from '../api/questions';
import { Difficulty } from '../types';
import { Lock, ShieldCheck, ArrowLeft, CheckCircle2 } from 'lucide-react';

export const CreateQuestion: React.FC = () => {
  const [content, setContent] = useState('');
  const [answer, setAnswer] = useState('');
  const [subject, setSubject] = useState('Computer Science');
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState<Difficulty>('MEDIUM');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const res = await questionsApi.create({
        content,
        answer,
        subject,
        topic,
        difficulty,
      });

      setSuccessMsg(`Question Q${res.id} encrypted & submitted into pipeline!`);
      setTimeout(() => navigate('/questions'), 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to submit question');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell title="Create Question" subtitle="Submit single question into envelope-encrypted storage">
      <div className="max-w-3xl space-y-6">
        <button
          onClick={() => navigate('/questions')}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Question Bank</span>
        </button>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Lock className="w-4 h-4 text-blue-600" />
              <span>Question Submission Form</span>
            </h3>

            {successMsg && (
              <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-xs font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{successMsg}</span>
              </div>
            )}

            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-xl text-xs font-semibold">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Question Content</label>
                <textarea
                  required
                  rows={4}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Enter the full question prompt text..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-900 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Correct Answer</label>
                <input
                  type="text"
                  required
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Enter correct answer"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Subject</label>
                  <input
                    type="text"
                    required
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Topic</label>
                  <input
                    type="text"
                    required
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g. Algorithms"
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-900 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Difficulty Level</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value as Difficulty)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs font-semibold text-slate-900"
                >
                  <option value="EASY">EASY</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HARD">HARD</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl text-xs shadow-md shadow-blue-500/20 transition-all disabled:opacity-50"
              >
                {isSubmitting ? 'Encrypting & Submitting...' : 'Encrypt & Submit Question'}
              </button>
            </form>
          </div>

          <div className="bg-slate-900 text-white border border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-xl bg-blue-600/20 text-blue-400 flex items-center justify-center mb-4">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h4 className="font-extrabold text-sm mb-2">Zero-Trust Isolation</h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Question setters operate at single-question granularity. Your credentials do not grant access to view the complete question bank or candidate exam papers.
              </p>
            </div>

            <div className="p-3.5 bg-slate-800/80 border border-slate-700/80 rounded-xl text-[11px] text-slate-300">
              🔒 <strong>Cryptographic Guarantee:</strong> Content is encrypted with AES-256-GCM. SHA-256 integrity hash is logged to the blockchain ledger.
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
};
