import { apiFetch } from './client';
import { User } from '../types';

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  login: (email: string, password: string) =>
    apiFetch<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  register: (name: string, email: string, password: string, role: string) =>
    apiFetch<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password, role }),
    }),
};
