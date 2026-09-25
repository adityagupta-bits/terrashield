import { create } from 'zustand';

interface AuthState {
  token: string | null;
  email: string | null;
  role: 'authority' | 'viewer' | null;
  isAuthenticated: boolean;
  login: (token: string, email: string, role: 'authority' | 'viewer') => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('terrashield_token'),
  email: localStorage.getItem('terrashield_email'),
  role: (localStorage.getItem('terrashield_role') as 'authority' | 'viewer') || null,
  isAuthenticated: !!localStorage.getItem('terrashield_token'),
  login: (token, email, role) => {
    localStorage.setItem('terrashield_token', token);
    localStorage.setItem('terrashield_email', email);
    localStorage.setItem('terrashield_role', role);
    set({ token, email, role, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('terrashield_token');
    localStorage.removeItem('terrashield_email');
    localStorage.removeItem('terrashield_role');
    set({ token: null, email: null, role: null, isAuthenticated: false });
  }
}));
