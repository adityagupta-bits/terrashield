import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

export function useNodes() {
  return useQuery({
    queryKey: ['nodes'],
    queryFn: () => api.getNodes(),
    refetchInterval: 8000
  });
}

export function useNode(id: string | number) {
  return useQuery({
    queryKey: ['node', id],
    queryFn: () => api.getNode(id),
    enabled: !!id
  });
}

export function useNodeReadings(id: string | number, limit = 50) {
  return useQuery({
    queryKey: ['readings', id, limit],
    queryFn: () => api.getNodeReadings(id, limit),
    enabled: !!id,
    refetchInterval: 4000
  });
}

export function useAlerts(params?: { status?: string; severity?: string; hazard_type?: string }) {
  return useQuery({
    queryKey: ['alerts', params],
    queryFn: () => api.getAlerts(params),
    refetchInterval: 5000
  });
}

export function useContacts(near?: string, category?: string) {
  return useQuery({
    queryKey: ['contacts', near, category],
    queryFn: () => api.getContacts(near, category)
  });
}

export function useWeather(lat = 30.0869, lng = 78.2676) {
  return useQuery({
    queryKey: ['weather', lat, lng],
    queryFn: () => api.getCurrentWeather(lat, lng),
    staleTime: 600000 // 10 minutes
  });
}

export function useWeatherForecast() {
  return useQuery({
    queryKey: ['weather_forecast'],
    queryFn: () => api.getWeatherForecast(),
    staleTime: 600000
  });
}

export function useMultiHazardRisk(horizonDays = 7) {
  return useQuery({
    queryKey: ['multi_hazard_risk', horizonDays],
    queryFn: () => api.getMultiHazardRisk(horizonDays),
    staleTime: 300000
  });
}

export function useNews() {
  return useQuery({
    queryKey: ['news'],
    queryFn: () => api.getNews(),
    staleTime: 60000
  });
}

export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: () => api.getStats(),
    refetchInterval: 5000
  });
}

export function useZones() {
  return useQuery({
    queryKey: ['zones'],
    queryFn: () => api.getZones(),
    staleTime: 300000
  });
}

export function useMeshTopology() {
  return useQuery({
    queryKey: ['mesh_topology'],
    queryFn: () => api.getMeshTopology(),
    refetchInterval: 8000
  });
}

export function useCitizenStatus(lat: number, lng: number, lang = 'en') {
  return useQuery({
    queryKey: ['citizen_status', lat, lng, lang],
    queryFn: () => api.getCitizenStatus(lat, lng, lang),
    enabled: !isNaN(lat) && !isNaN(lng)
  });
}
