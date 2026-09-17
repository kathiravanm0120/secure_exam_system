import { apiFetch } from './client';
import { InvestigationResult, FingerprintMatch } from '../types';

export const investigationApi = {
  analyzeLeak: (suspectedText: string, examId?: number, documentHash?: string) =>
    apiFetch<InvestigationResult>('/investigation/analyze', {
      method: 'POST',
      body: JSON.stringify({
        suspected_text: suspectedText,
        exam_id: examId || null,
        document_hash: documentHash || null,
      }),
    }),

  getQuestionLifecycle: (questionId: number) =>
    apiFetch<{
      question_id: number;
      current_status: string;
      exposure_count: number;
      exposure_status: string;
      timeline_events_count: number;
      timeline: {
        stage: string;
        timestamp: string | null;
        actor: string;
        actor_role: string;
        source: string;
        details: string;
        blockchain_ref: string;
      }[];
      blockchain_events: any[];
    }>(`/investigation/questions/${questionId}/lifecycle`),

  matchFingerprint: (suspectedText: string, examId?: number) =>
    apiFetch<FingerprintMatch>('/fingerprints/match', {
      method: 'POST',
      body: JSON.stringify({
        suspected_text: suspectedText,
        exam_id: examId || null,
      }),
    }),
};
