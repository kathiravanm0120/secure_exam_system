import { apiFetch } from './client';

export const blockchainApi = {
  verifyChain: () => apiFetch<{ valid: boolean; blocks?: number; last_hash?: string; bad_index?: number; reason?: string }>('/blockchain/verify'),

  getChain: () => apiFetch<{ chain: any[] }>('/blockchain/chain'),

  verifyQuestion: (questionId: number) =>
    apiFetch<{
      question_id: number;
      database_hash: string;
      current_content_hash: string;
      content_integrity: boolean;
      blockchain_record_found: boolean;
      event_count: number;
      events: any[];
      blockchain: { valid: boolean };
    }>(`/blockchain/questions/${questionId}/verify`),
};
