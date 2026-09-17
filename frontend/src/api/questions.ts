import { apiFetch } from './client';
import { Question, QuestionStatus, Difficulty } from '../types';

export interface CreateQuestionPayload {
  content: string;
  answer: string;
  subject: string;
  topic: string;
  difficulty: Difficulty;
}

export interface ReviewQuestionPayload {
  decision: 'APPROVE' | 'REJECT';
  comments?: string;
}

export const questionsApi = {
  create: (data: CreateQuestionPayload) =>
    apiFetch<Question>('/questions', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getMyQuestions: () => apiFetch<Question[]>('/questions/my'),

  assignReviewer: (questionId: number, reviewerId: number) =>
    apiFetch<Question>(`/questions/${questionId}/assign/${reviewerId}`, {
      method: 'POST',
    }),

  review: (questionId: number, data: ReviewQuestionPayload) =>
    apiFetch<Question>(`/questions/${questionId}/review`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
