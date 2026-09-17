import React, { useState, useEffect } from 'react';
import { examsApi, CbtHeaders } from '../api/exams';
import { CandidateQuestion, ExamSession } from '../types';
import { ShieldCheck, Clock, Send, AlertCircle, Wifi, CheckCircle2 } from 'lucide-react';

export const CBT: React.FC = () => {
  const [examId, setExamId] = useState('2');
  const [centreId, setCentreId] = useState('1');
  const [deviceId, setDeviceId] = useState('DEV-0001');
  const [deviceToken, setDeviceToken] = useState('SECURE_DEV_TOKEN_0001');

  const [session, setSession] = useState<ExamSession | null>(null);
  const [currentPos, setCurrentPos] = useState(1);
  const [currentQuestion, setCurrentQuestion] = useState<CandidateQuestion | null>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [answerInput, setAnswerInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [timeLeft, setTimeLeft] = useState(3600); // 1 hour timer
  const [isFinished, setIsFinished] = useState(false);

  const cbtHeaders: CbtHeaders = {
    centreId,
    deviceId,
    deviceToken,
    sessionToken: session?.session_token || undefined,
  };

  // Timer countdown
  useEffect(() => {
    if (!session || isFinished) return;
    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          handleFinish();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [session, isFinished]);

  // Periodic Heartbeat every 30 seconds
  useEffect(() => {
    if (!session || isFinished) return;
    const interval = setInterval(async () => {
      try {
        await examsApi.heartbeat(Number(examId), cbtHeaders);
      } catch (err) {
        console.error('Heartbeat failed', err);
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [session, isFinished]);

  const handleStartCbt = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const res = await examsApi.startCbtSession(Number(examId), cbtHeaders);
      setSession(res);
      setIsFinished(false);
      await loadQuestionPosition(1, res);
    } catch (err: any) {
      setError(err.message || 'Failed to start CBT session');
    } finally {
      setIsLoading(false);
    }
  };

  const loadQuestionPosition = async (pos: number, activeSession: ExamSession | null = session) => {
    if (!activeSession) return;
    setCurrentPos(pos);
    setIsLoading(true);
    setError(null);
    try {
      const headers: CbtHeaders = {
        centreId,
        deviceId,
        deviceToken,
        sessionToken: activeSession.session_token || undefined,
      };
      const q = await examsApi.getQuestionPosition(activeSession.exam_id, pos, headers);
      setCurrentQuestion(q);
      setAnswerInput(answers[pos] || '');
    } catch (err: any) {
      setError(err.message || 'Failed to load question');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveAnswer = async () => {
    if (!session || !currentQuestion) return;
    if (!answerInput.trim()) {
      navNext();
      return;
    }

    setIsLoading(true);
    const nonce = 'NONCE_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
    try {
      await examsApi.submitAnswer(session.exam_id, currentQuestion.question_id, answerInput, nonce, cbtHeaders);
      setAnswers({ ...answers, [currentPos]: answerInput });
      navNext();
    } catch (err: any) {
      setError(err.message || 'Failed to save answer');
    } finally {
      setIsLoading(false);
    }
  };

  const navNext = () => {
    if (session && currentPos < session.question_count) {
      loadQuestionPosition(currentPos + 1);
    }
  };

  const navPrev = () => {
    if (currentPos > 1) {
      loadQuestionPosition(currentPos - 1);
    }
  };

  const handleFinish = async () => {
    if (!session) return;
    if (!confirm('Are you sure you want to submit your final examination?')) return;
    setIsLoading(true);
    try {
      await examsApi.finishCbtSession(session.exam_id, cbtHeaders);
      setIsFinished(true);
      setSession(null);
    } catch (err: any) {
      setError(err.message || 'Failed to finish exam');
    } finally {
      setIsLoading(false);
    }
  };

  const formatTimer = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  if (isFinished) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center shadow-2xl">
          <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center mx-auto mb-4 font-bold text-2xl">
            ✓
          </div>
          <h2 className="text-xl font-bold mb-2">Examination Submitted</h2>
          <p className="text-xs text-slate-400 mb-6">
            Your answers have been cryptographically hashed and logged to the central audit ledger.
          </p>
          <button
            onClick={() => (window.location.href = '/dashboard')}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl text-xs"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 text-blue-400 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Candidate CBT Portal</h2>
              <p className="text-xs text-slate-400">Device-bound examination session</p>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-xs font-semibold flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleStartCbt} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-300 font-bold mb-1">Exam ID</label>
              <input
                type="number"
                required
                value={examId}
                onChange={(e) => setExamId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-white"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-bold mb-1">Centre ID</label>
              <input
                type="number"
                required
                value={centreId}
                onChange={(e) => setCentreId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-white"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-bold mb-1">Device Code</label>
              <input
                type="text"
                required
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-white"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-bold mb-1">Device Token</label>
              <input
                type="text"
                required
                value={deviceToken}
                onChange={(e) => setDeviceToken(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-2.5 text-white"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-600/20 transition-all disabled:opacity-50"
            >
              {isLoading ? 'Authorizing CBT Session...' : 'Start Candidate CBT Exam'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col">
      {/* Top Examination Bar */}
      <header className="bg-slate-950 border-b border-slate-800 px-6 py-3.5 flex justify-between items-center sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-xs">
            SE
          </div>
          <div>
            <h1 className="text-xs font-bold text-white">Candidate Examination Interface</h1>
            <span className="text-[10px] text-slate-400">Exam #{session.exam_id} · Bound to {deviceId}</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-xs font-bold">
            <Wifi className="w-3.5 h-3.5" />
            <span>CONNECTED</span>
          </div>

          <div className="flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-800 border border-slate-700 rounded-xl text-xs font-mono font-bold text-amber-400">
            <Clock className="w-4 h-4" />
            <span>{formatTimer(timeLeft)}</span>
          </div>

          <button
            onClick={handleFinish}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl text-xs transition-colors shadow-sm"
          >
            Submit & Finish Exam
          </button>
        </div>
      </header>

      {/* Main CBT Workspace */}
      <main className="flex-1 p-6 max-w-6xl mx-auto w-full grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Question Panel */}
        <div className="lg:col-span-3 bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 flex flex-col justify-between shadow-xl">
          <div>
            <div className="flex justify-between items-center mb-4">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Question {currentPos} of {session.question_count}
              </span>
              <span className="text-xs font-bold text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-full border border-blue-500/20">
                {currentQuestion?.topic} ({currentQuestion?.difficulty})
              </span>
            </div>

            {isLoading ? (
              <div className="py-16 text-center text-slate-400 text-xs font-medium">Fetching question JIT...</div>
            ) : currentQuestion ? (
              <div className="space-y-6">
                <div className="text-sm font-semibold text-slate-100 leading-relaxed bg-slate-900/60 p-5 rounded-xl border border-slate-800">
                  {currentQuestion.content}
                </div>

                <div className="space-y-2">
                  <label className="block text-xs font-bold text-slate-300">Your Answer</label>
                  <textarea
                    rows={4}
                    value={answerInput}
                    onChange={(e) => setAnswerInput(e.target.value)}
                    placeholder="Type your answer response here..."
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3.5 text-xs text-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
            ) : null}
          </div>

          <div className="flex justify-between items-center pt-6 border-t border-slate-700/80 mt-6">
            <button
              onClick={navPrev}
              disabled={currentPos <= 1 || isLoading}
              className="px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl text-xs disabled:opacity-40"
            >
              ← Previous
            </button>

            <button
              onClick={handleSaveAnswer}
              disabled={isLoading}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-xs shadow-md shadow-blue-600/20 flex items-center gap-1.5 disabled:opacity-40"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Save & Next →</span>
            </button>
          </div>
        </div>

        {/* Question Palette Sidebar */}
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 flex flex-col justify-between shadow-xl">
          <div>
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4">Question Navigator</h3>
            <div className="grid grid-cols-4 gap-2">
              {Array.from({ length: session.question_count }).map((_, idx) => {
                const p = idx + 1;
                const isAnswered = !!answers[p];
                const isCurrent = p === currentPos;
                return (
                  <button
                    key={p}
                    onClick={() => loadQuestionPosition(p)}
                    className={`h-10 rounded-xl text-xs font-extrabold transition-all border ${
                      isCurrent
                        ? 'bg-blue-600 text-white border-blue-400 shadow-md shadow-blue-600/30'
                        : isAnswered
                        ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                        : 'bg-slate-900 text-slate-400 border-slate-700 hover:bg-slate-700'
                    }`}
                  >
                    {p}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-700/80 text-[11px] text-slate-400 space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-600" /> Current Question
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/40" /> Saved Answer
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-slate-900" /> Unanswered
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
