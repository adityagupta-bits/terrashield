import { create } from 'zustand';

interface UIState {
  selectedNodeId: string;
  activeAlertId: number | null;
  demoMode: boolean;
  language: 'en' | 'hi';
  mapCenter: [number, number];
  mapZoom: number;
  setSelectedNodeId: (id: string) => void;
  setActiveAlertId: (id: number | null) => void;
  setDemoMode: (enabled: boolean) => void;
  setLanguage: (lang: 'en' | 'hi') => void;
  setMapCenter: (center: [number, number], zoom?: number) => void;
}

export const useUIStore = create<UIState>((set) => ({
  selectedNodeId: 'PHY-01',
  activeAlertId: null,
  demoMode: true,
  language: (localStorage.getItem('terrashield_lang') as 'en' | 'hi') || 'en',
  mapCenter: [30.0869, 78.2676],
  mapZoom: 12,
  setSelectedNodeId: (id) => set({ selectedNodeId: id }),
  setActiveAlertId: (id) => set({ activeAlertId: id }),
  setDemoMode: (enabled) => set({ demoMode: enabled }),
  setLanguage: (lang) => {
    localStorage.setItem('terrashield_lang', lang);
    set({ language: lang });
  },
  setMapCenter: (center, zoom) => set((state) => ({
    mapCenter: center,
    mapZoom: zoom !== undefined ? zoom : state.mapZoom
  }))
}));
