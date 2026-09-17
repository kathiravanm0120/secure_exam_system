import { apiFetch } from './client';
import { SecurityAlert, SecurityEvent } from '../types';

export const securityApi = {
  getAlerts: () => apiFetch<SecurityAlert[]>('/security/alerts'),

  getAlertById: (id: number) => apiFetch<SecurityAlert>(`/security/alerts/${id}`),

  resolveAlert: (id: number) =>
    apiFetch<SecurityAlert>(`/security/alerts/${id}/resolve`, {
      method: 'POST',
    }),

  getCandidateEvents: (candidateId: number) =>
    apiFetch<SecurityEvent[]>(`/security/events/${candidateId}`),
};
