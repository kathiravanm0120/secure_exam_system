import { apiFetch } from './client';
import {
  Exam,
  BlueprintRule,
  ReleaseStatus,
  ReleaseApproval,
  ExamSession,
  CandidateQuestion,
  PaperValidationReport,
  ExposureOut,
} from '../types';

export interface CreateExamPayload {
  name: string;
  subject: string;
  starts_at: string;
  ends_at: string;
  rules: BlueprintRule[];
}

export interface CbtHeaders {
  centreId: number | string;
  deviceId: string;
  deviceToken: string;
  sessionToken?: string;
}

export const examsApi = {
  create: (data: CreateExamPayload) =>
    apiFetch<Exam>('/exams', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getById: (id: number) => apiFetch<Exam>(`/exams/${id}`),

  getReleaseStatus: (id: number) => apiFetch<ReleaseStatus>(`/exams/${id}/release-status`),

  approveRelease: (id: number, deviceId?: string) =>
    apiFetch<ReleaseApproval>(`/exams/${id}/release/approve`, {
      method: 'POST',
      headers: deviceId ? { 'X-Exam-Device-ID': deviceId } : {},
    }),

  release: (id: number) =>
    apiFetch<ReleaseStatus>(`/exams/${id}/release`, {
      method: 'POST',
    }),

  validatePaper: (id: number) => apiFetch<PaperValidationReport>(`/exams/${id}/validate`),

  startCbtSession: (examId: number, cbt: CbtHeaders) =>
    apiFetch<ExamSession>(`/exams/${examId}/start`, {
      method: 'POST',
      headers: {
        'X-Exam-Centre-ID': String(cbt.centreId),
        'X-Exam-Device-ID': cbt.deviceId,
        'X-Exam-Device-Token': cbt.deviceToken,
      },
    }),

  getQuestionPosition: (examId: number, position: number, cbt: CbtHeaders) =>
    apiFetch<CandidateQuestion>(`/exams/${examId}/questions/${position}`, {
      headers: {
        'X-Exam-Session-Token': cbt.sessionToken || '',
        'X-Exam-Device-ID': cbt.deviceId,
        'X-Exam-Device-Token': cbt.deviceToken,
        'X-Exam-Centre-ID': String(cbt.centreId),
      },
    }),

  submitAnswer: (examId: number, questionId: number, answer: string, nonce: string, cbt: CbtHeaders) =>
    apiFetch<{ question_id: number; submitted_at: string; updated: boolean }>(`/exams/${examId}/answers`, {
      method: 'POST',
      headers: {
        'X-Exam-Session-Token': cbt.sessionToken || '',
        'X-Exam-Device-ID': cbt.deviceId,
        'X-Exam-Device-Token': cbt.deviceToken,
        'X-Exam-Centre-ID': String(cbt.centreId),
      },
      body: JSON.stringify({
        question_id: questionId,
        answer,
        client_nonce: nonce,
      }),
    }),

  heartbeat: (examId: number, cbt: CbtHeaders) =>
    apiFetch<ExamSession>(`/exams/${examId}/heartbeat`, {
      method: 'POST',
      headers: {
        'X-Exam-Session-Token': cbt.sessionToken || '',
        'X-Exam-Device-ID': cbt.deviceId,
        'X-Exam-Device-Token': cbt.deviceToken,
        'X-Exam-Centre-ID': String(cbt.centreId),
      },
    }),

  finishCbtSession: (examId: number, cbt: CbtHeaders) =>
    apiFetch<ExamSession>(`/exams/${examId}/finish`, {
      method: 'POST',
      headers: {
        'X-Exam-Session-Token': cbt.sessionToken || '',
        'X-Exam-Device-ID': cbt.deviceId,
        'X-Exam-Device-Token': cbt.deviceToken,
        'X-Exam-Centre-ID': String(cbt.centreId),
      },
    }),

  getExposures: () => apiFetch<ExposureOut[]>('/exams/exposure/questions'),
};
