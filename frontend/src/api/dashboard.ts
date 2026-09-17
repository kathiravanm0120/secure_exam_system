import { apiFetch } from './client';
import { DashboardSummary } from '../types';

export const dashboardApi = {
  getSummary: () => apiFetch<DashboardSummary>('/dashboard/summary'),
};
