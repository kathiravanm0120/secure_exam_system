import React, { useEffect, useState } from 'react';
import { blockchainApi } from '../api/blockchain';
import { ShieldCheck, AlertTriangle, Database, CheckCircle, RefreshCw, Key } from 'lucide-react';

export const Blockchain: React.FC = () => {
  const [chainState, setChainState] = useState<{ valid: boolean; blocks?: number; last_hash?: string; bad_index?: number; reason?: string } | null>(null);
  const [blocks, setBlocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [questionId, setQuestionId] = useState('');
  const [questionVerification, setQuestionVerification] = useState<any>(null);
  const [verifyingQ, setVerifyingQ] = useState(false);

  const fetchChain = async () => {
    setLoading(true);
    setError('');
    try {
      const [resStatus, resChain] = await Promise.all([
        blockchainApi.verifyChain(),
        blockchainApi.getChain(),
      ]);
      setChainState(resStatus);
      setBlocks(resChain.chain || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch blockchain data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChain();
  }, []);

  const handleVerifyQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!questionId) return;
    setVerifyingQ(true);
    setQuestionVerification(null);
    try {
      const res = await blockchainApi.verifyQuestion(Number(questionId));
      setQuestionVerification(res);
    } catch (err: any) {
      alert('Verification failed: ' + err.message);
    } finally {
      setVerifyingQ(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Blockchain Audit Ledger</h1>
          <p className="text-gray-600">Cryptographically verifiable immutable audit trail for all exam lifecycle operations.</p>
        </div>
        <button
          onClick={fetchChain}
          disabled={loading}
          className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Verify & Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg">
          {error}
        </div>
      )}

      {/* Ledger Integrity Card */}
      {chainState && (
        <div className={`p-6 rounded-xl border ${chainState.valid ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200'}`}>
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-4">
              <div className={`p-3 rounded-xl ${chainState.valid ? 'bg-emerald-500 text-white' : 'bg-rose-500 text-white'}`}>
                {chainState.valid ? <ShieldCheck className="w-8 h-8" /> : <AlertTriangle className="w-8 h-8" />}
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">
                  {chainState.valid ? 'Ledger Integrity Verified' : 'Ledger Tamper Detected!'}
                </h3>
                <p className="text-sm text-gray-600">
                  {chainState.valid
                    ? `All ${chainState.blocks} block hashes and merkle roots match expected values.`
                    : `Corruption at block #${chainState.bad_index}: ${chainState.reason}`}
                </p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs text-gray-500 uppercase tracking-wider block">Latest Hash</span>
              <code className="text-xs bg-white px-2 py-1 rounded border font-mono text-gray-700 max-w-xs block truncate">
                {chainState.last_hash || 'N/A'}
              </code>
            </div>
          </div>
        </div>
      )}

      {/* Question Verification Search */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-4">
        <h3 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
          <Key className="w-5 h-5 text-indigo-600" />
          <span>Verify Individual Question Provenance</span>
        </h3>
        <form onSubmit={handleVerifyQuestion} className="flex space-x-4">
          <input
            type="number"
            placeholder="Enter Question ID (e.g. 1)"
            value={questionId}
            onChange={(e) => setQuestionId(e.target.value)}
            className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            required
          />
          <button
            type="submit"
            disabled={verifyingQ}
            className="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
          >
            {verifyingQ ? 'Verifying...' : 'Verify Question'}
          </button>
        </form>

        {questionVerification && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-3 border text-sm">
            <div className="flex justify-between items-center">
              <span className="font-semibold text-gray-700">Content Integrity Match:</span>
              <span className={`px-2 py-1 rounded text-xs font-bold ${questionVerification.content_integrity ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                {questionVerification.content_integrity ? 'VALID / MATCHED' : 'TAMPERED / MISMATCH'}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4 text-xs font-mono bg-white p-3 rounded border">
              <div>
                <span className="text-gray-500 block">Database Hash:</span>
                <span className="text-gray-800 truncate block">{questionVerification.database_hash}</span>
              </div>
              <div>
                <span className="text-gray-500 block">Current Content Hash:</span>
                <span className="text-gray-800 truncate block">{questionVerification.current_content_hash}</span>
              </div>
            </div>
            <div>
              <span className="font-semibold text-gray-700 block mb-2">Audit Events ({questionVerification.event_count}):</span>
              <div className="space-y-1 max-h-40 overflow-y-auto">
                {questionVerification.events?.map((ev: any, idx: number) => (
                  <div key={idx} className="p-2 bg-white rounded border text-xs flex justify-between">
                    <span className="font-medium text-indigo-600">{ev.event_type}</span>
                    <span className="text-gray-500">{new Date(ev.timestamp).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Block Trail */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-4">
        <h3 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
          <Database className="w-5 h-5 text-indigo-600" />
          <span>Block Chain Explorer ({blocks.length} Blocks)</span>
        </h3>
        
        <div className="space-y-4">
          {blocks.map((block: any) => (
            <div key={block.index} className="p-4 border rounded-xl hover:border-indigo-300 transition bg-slate-50/50">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-1 bg-indigo-100 text-indigo-800 font-bold text-xs rounded">
                    Block #{block.index}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(block.timestamp).toLocaleString()}
                  </span>
                </div>
                <span className="text-xs text-emerald-600 font-semibold flex items-center space-x-1">
                  <CheckCircle className="w-3.5 h-3.5" />
                  <span>Verified</span>
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono text-gray-600 mb-3 bg-white p-2 rounded border">
                <div>
                  <span className="text-gray-400 block">Hash:</span>
                  <span className="truncate block font-semibold text-gray-800">{block.hash}</span>
                </div>
                <div>
                  <span className="text-gray-400 block">Prev Hash:</span>
                  <span className="truncate block">{block.prev_hash}</span>
                </div>
              </div>

              <div>
                <span className="text-xs font-medium text-gray-700 block mb-1">
                  Transactions ({block.transactions?.length || 0}):
                </span>
                <div className="space-y-1">
                  {block.transactions?.map((tx: any, txIdx: number) => (
                    <div key={txIdx} className="text-xs bg-white p-2 rounded border flex items-center justify-between">
                      <span className="font-bold text-gray-800">{tx.event_type}</span>
                      <pre className="text-[10px] text-gray-500 font-mono overflow-x-auto max-w-lg">
                        {JSON.stringify(tx.payload || tx.data || {})}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
