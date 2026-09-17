import { apiFetch } from './client';
import { ExamCentre, CentreDevice, CandidateAssignment } from '../types';

export const identityApi = {
  createCentre: (code: string, name: string) =>
    apiFetch<ExamCentre>('/identity/centres', {
      method: 'POST',
      body: JSON.stringify({ code, name }),
    }),

  registerDevice: (centreId: number, deviceCode: string) =>
    apiFetch<CentreDevice>(`/identity/centres/${centreId}/devices`, {
      method: 'POST',
      body: JSON.stringify({ device_code: deviceCode }),
    }),

  assignCentreToExam: (examId: number, centreId: number) =>
    apiFetch<{ id: number; exam_id: number; centre_id: number; status: string }>(
      `/identity/exams/${examId}/centres?centre_id=${centreId}`,
      { method: 'POST' }
    ),

  assignCandidate: (examId: number, candidateId: number, centreId: number, seatNumber?: string, identityRef?: string) =>
    apiFetch<CandidateAssignment>(`/identity/exams/${examId}/candidates`, {
      method: 'POST',
      body: JSON.stringify({
        candidate_id: candidateId,
        centre_id: centreId,
        seat_number: seatNumber,
        identity_reference: identityRef,
      }),
    }),

  verifyCandidate: (examId: number, candidateId: number) =>
    apiFetch<CandidateAssignment>(`/identity/exams/${examId}/candidates/${candidateId}/verify`, {
      method: 'POST',
    }),

  getCandidateAssignment: (examId: number, candidateId: number) =>
    apiFetch<CandidateAssignment>(`/identity/exams/${examId}/candidates/${candidateId}`),
};
