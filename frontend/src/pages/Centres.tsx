import React, { useState } from 'react';
import { identityApi } from '../api/identity';
import { Building2, Laptop, UserCheck, Shield, Key, CheckCircle, AlertCircle } from 'lucide-react';

export const Centres: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'create_centre' | 'register_device' | 'assign_centre' | 'assign_candidate' | 'verify_candidate'>('create_centre');

  // Form states
  const [centreCode, setCentreCode] = useState('');
  const [centreName, setCentreName] = useState('');
  
  const [deviceCentreId, setDeviceCentreId] = useState('');
  const [deviceCode, setDeviceCode] = useState('');
  const [generatedToken, setGeneratedToken] = useState<{ device_code: string; device_token: string } | null>(null);

  const [assignExamId, setAssignExamId] = useState('');
  const [assignCentreId, setAssignCentreId] = useState('');

  const [candExamId, setCandExamId] = useState('');
  const [candId, setCandId] = useState('');
  const [candCentreId, setCandCentreId] = useState('');
  const [seatNumber, setSeatNumber] = useState('');
  const [identityRef, setIdentityRef] = useState('');

  const [verifyExamId, setVerifyExamId] = useState('');
  const [verifyCandId, setVerifyCandId] = useState('');
  const [verifyResult, setVerifyResult] = useState<any>(null);

  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleCreateCentre = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      const res = await identityApi.createCentre(centreCode, centreName);
      setMessage({ type: 'success', text: `Exam Centre "${res.name}" (Code: ${res.code}) created successfully!` });
      setCentreCode('');
      setCentreName('');
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to create centre' });
    }
  };

  const handleRegisterDevice = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setGeneratedToken(null);
    try {
      const res = await identityApi.registerDevice(Number(deviceCentreId), deviceCode);
      setGeneratedToken({ device_code: res.device_code, device_token: res.device_token || '' });
      setMessage({ type: 'success', text: `Device "${res.device_code}" registered!` });
      setDeviceCode('');
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to register device' });
    }
  };

  const handleAssignCentre = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      await identityApi.assignCentreToExam(Number(assignExamId), Number(assignCentreId));
      setMessage({ type: 'success', text: `Centre ${assignCentreId} assigned to Exam ${assignExamId} successfully!` });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to assign centre to exam' });
    }
  };

  const handleAssignCandidate = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      const res = await identityApi.assignCandidate(
        Number(candExamId),
        Number(candId),
        Number(candCentreId),
        seatNumber || undefined,
        identityRef || undefined
      );
      setMessage({ type: 'success', text: `Candidate #${res.candidate_id} assigned to Seat ${res.seat_number || 'N/A'} at Centre ${res.centre_id}.` });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to assign candidate' });
    }
  };

  const handleVerifyCandidate = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setVerifyResult(null);
    try {
      const res = await identityApi.verifyCandidate(Number(verifyExamId), Number(verifyCandId));
      setVerifyResult(res);
      setMessage({ type: 'success', text: `Candidate ID #${res.candidate_id} verification status: ${res.identity_status}` });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to verify candidate' });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Exam Centres & Device Provisioning</h1>
        <p className="text-gray-600">Register test centres, provision secure hardware tokens, assign candidates, and verify biometrics/ID.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 space-x-4">
        {[
          { id: 'create_centre', label: 'Create Centre', icon: Building2 },
          { id: 'register_device', label: 'Provision Device', icon: Laptop },
          { id: 'assign_centre', label: 'Assign Centre to Exam', icon: Shield },
          { id: 'assign_candidate', label: 'Seat Candidate', icon: UserCheck },
          { id: 'verify_candidate', label: 'Verify Identity', icon: Key },
        ].map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id as any);
                setMessage(null);
              }}
              className={`flex items-center space-x-2 py-3 px-4 text-sm font-medium border-b-2 transition ${
                active ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {message && (
        <div className={`p-4 rounded-lg flex items-center space-x-2 ${message.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-800 border border-red-200'}`}>
          {message.type === 'success' ? <CheckCircle className="w-5 h-5 text-emerald-600" /> : <AlertCircle className="w-5 h-5 text-red-600" />}
          <span className="text-sm">{message.text}</span>
        </div>
      )}

      {/* Form Panels */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 max-w-2xl">
        {activeTab === 'create_centre' && (
          <form onSubmit={handleCreateCentre} className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Register New Examination Centre</h3>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Centre Code</label>
              <input
                type="text"
                placeholder="e.g. CTR-002"
                value={centreCode}
                onChange={(e) => setCentreCode(e.target.value)}
                className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Centre Name</label>
              <input
                type="text"
                placeholder="e.g. Main Science Lab Centre B"
                value={centreName}
                onChange={(e) => setCentreName(e.target.value)}
                className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                required
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2.5 bg-indigo-600 text-white font-medium text-sm rounded-lg hover:bg-indigo-700 transition"
            >
              Register Centre
            </button>
          </form>
        )}

        {activeTab === 'register_device' && (
          <form onSubmit={handleRegisterDevice} className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Provision Secure Workstation / Device</h3>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Centre ID</label>
              <input
                type="number"
                placeholder="e.g. 1"
                value={deviceCentreId}
                onChange={(e) => setDeviceCentreId(e.target.value)}
                className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Device Hardware Code</label>
              <input
                type="text"
                placeholder="e.g. DEV-0002"
                value={deviceCode}
                onChange={(e) => setDeviceCode(e.target.value)}
                className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                required
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2.5 bg-indigo-600 text-white font-medium text-sm rounded-lg hover:bg-indigo-700 transition"
            >
              Provision Device Token
            </button>

            {generatedToken && (
              <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg space-y-2">
                <h4 className="text-xs font-bold text-amber-800 uppercase">Warning: Store Device Token Securely</h4>
                <p className="text-xs text-amber-700">This token will be sent in `X-Exam-Device-Token` header for CBT workstation verification.</p>
                <div className="p-2 bg-white border rounded text-xs font-mono text-gray-800 break-all select-all">
                  {generatedToken.device_token}
                </div>
              </div>
            )}
          </form>
        )}

        {activeTab === 'assign_centre' && (
          <form onSubmit={handleAssignCentre} className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Assign Centre to Active Examination</h3>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Exam ID</label>
              <input
                type="number"
                placeholder="e.g. 2"
                value={assignExamId}
                onChange={(e) => setAssignExamId(e.target.value)}
                className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Centre ID</label>
              <input
                type="number"
                placeholder="e.g. 1"
                value={assignCentreId}
                onChange={(e) => setAssignCentreId(e.target.value)}
                className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                required
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2.5 bg-indigo-600 text-white font-medium text-sm rounded-lg hover:bg-indigo-700 transition"
            >
              Assign Centre
            </button>
          </form>
        )}

        {activeTab === 'assign_candidate' && (
          <form onSubmit={handleAssignCandidate} className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Seat Candidate at Test Centre</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Exam ID</label>
                <input
                  type="number"
                  placeholder="e.g. 2"
                  value={candExamId}
                  onChange={(e) => setCandExamId(e.target.value)}
                  className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Candidate User ID</label>
                <input
                  type="number"
                  placeholder="e.g. 9"
                  value={candId}
                  onChange={(e) => setCandId(e.target.value)}
                  className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Centre ID</label>
                <input
                  type="number"
                  placeholder="e.g. 1"
                  value={candCentreId}
                  onChange={(e) => setCandCentreId(e.target.value)}
                  className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Seat Number</label>
                <input
                  type="text"
                  placeholder="e.g. A-12"
                  value={seatNumber}
                  onChange={(e) => setSeatNumber(e.target.value)}
                  className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Biometric / Identity Ref Code</label>
              <input
                type="text"
                placeholder="e.g. BIO-PASS-998822"
                value={identityRef}
                onChange={(e) => setIdentityRef(e.target.value)}
                className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2.5 bg-indigo-600 text-white font-medium text-sm rounded-lg hover:bg-indigo-700 transition"
            >
              Assign Candidate Seat
            </button>
          </form>
        )}

        {activeTab === 'verify_candidate' && (
          <form onSubmit={handleVerifyCandidate} className="space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Biometric & Photo ID Verification</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Exam ID</label>
                <input
                  type="number"
                  placeholder="e.g. 2"
                  value={verifyExamId}
                  onChange={(e) => setVerifyExamId(e.target.value)}
                  className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase mb-1">Candidate User ID</label>
                <input
                  type="number"
                  placeholder="e.g. 9"
                  value={verifyCandId}
                  onChange={(e) => setVerifyCandId(e.target.value)}
                  className="w-full border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>
            </div>
            <button
              type="submit"
              className="px-6 py-2.5 bg-emerald-600 text-white font-medium text-sm rounded-lg hover:bg-emerald-700 transition"
            >
              Verify Candidate & Authorize Admission
            </button>

            {verifyResult && (
              <div className="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-xs space-y-1">
                <p className="font-bold text-emerald-900">Verification Certificate Generated:</p>
                <p>Assignment ID: #{verifyResult.id}</p>
                <p>Status: <span className="font-bold text-emerald-700">{verifyResult.identity_status}</span></p>
                <p>Verified At: {new Date(verifyResult.verified_at).toLocaleString()}</p>
              </div>
            )}
          </form>
        )}
      </div>
    </div>
  );
};
