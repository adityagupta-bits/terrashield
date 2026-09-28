import { useAuthStore } from '../store/authStore';
import {
  NodeItem,
  AlertItem,
  ContactItem,
  WeatherCurrent,
  WeatherForecastData,
  MultiHazardRiskData,
  NewsItem,
  SystemStats,
  MeshTopologyData,
  CitizenStatus
} from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = useAuthStore.getState().token;
    const headers = new Headers(options.headers || {});

    if (token && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorJson = await response.json();
        errorDetail = errorJson.detail || errorJson.message || errorDetail;
      } catch (e) {
        // use fallback text
      }
      throw new Error(errorDetail);
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string): Promise<{ token: string; role: 'authority' | 'viewer'; email: string }> {
    return this.request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  // Nodes
  async getNodes(): Promise<NodeItem[]> {
    return this.request<NodeItem[]>('/api/v1/nodes');
  }

  async getNode(id: string | number): Promise<NodeItem> {
    return this.request<NodeItem>(`/api/v1/nodes/${id}`);
  }

  async getNodeReadings(id: string | number, limit = 50): Promise<any[]> {
    return this.request<any[]>(`/api/v1/nodes/${id}/readings?limit=${limit}`);
  }

  // Alerts
  async getAlerts(params?: { status?: string; severity?: string; hazard_type?: string }): Promise<AlertItem[]> {
    const q = new URLSearchParams();
    if (params?.status) q.append('status', params.status);
    if (params?.severity) q.append('severity', params.severity);
    if (params?.hazard_type) q.append('hazard_type', params.hazard_type);
    const qs = q.toString();
    return this.request<AlertItem[]>(`/api/v1/alerts${qs ? `?${qs}` : ''}`);
  }

  async updateAlertStatus(id: number, status: string): Promise<any> {
    return this.request(`/api/v1/alerts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    });
  }

  async deployNdrf(id: number): Promise<any> {
    return this.request(`/api/v1/alerts/${id}/deploy-ndrf`, {
      method: 'POST'
    });
  }

  // Broadcast
  async getBroadcastPreview(lat: number, lng: number, radiusKm: number): Promise<{ recipients_count: number; radius_km: number }> {
    return this.request(`/api/v1/alerts/broadcast/preview?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`);
  }

  async sendBroadcast(payload: { lat: number; lng: number; radius_km: number; template_id: string }): Promise<any> {
    return this.request('/api/v1/alerts/broadcast', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Mesh Topology
  async getMeshTopology(): Promise<MeshTopologyData> {
    return this.request<MeshTopologyData>('/api/v1/mesh/topology');
  }

  async toggleBlackout(enabled: boolean): Promise<any> {
    return this.request(`/api/v1/mesh/blackout?enabled=${enabled}`, {
      method: 'POST'
    });
  }

  // Hazard Zones GeoJSON
  async getZones(): Promise<any> {
    return this.request('/api/v1/zones');
  }

  // Contacts
  async getContacts(near?: string, category?: string): Promise<ContactItem[]> {
    const q = new URLSearchParams();
    if (near) q.append('near', near);
    if (category) q.append('category', category);
    const qs = q.toString();
    return this.request<ContactItem[]>(`/api/v1/contacts${qs ? `?${qs}` : ''}`);
  }

  // Weather
  async getCurrentWeather(lat = 26.1850, lng = 91.7500): Promise<WeatherCurrent> {
    return this.request<WeatherCurrent>(`/api/v1/weather/current?lat=${lat}&lng=${lng}`);
  }

  async getWeatherForecast(): Promise<WeatherForecastData> {
    return this.request<WeatherForecastData>('/api/v1/weather/forecast');
  }

  async getMultiHazardRisk(horizonDays = 7, lat = 26.1850, lng = 91.7500): Promise<MultiHazardRiskData> {
    return this.request<MultiHazardRiskData>(`/api/v1/weather/multi-hazard-risk?horizon_days=${horizonDays}&lat=${lat}&lng=${lng}`);
  }

  async getHistoricalWeather(limit = 100): Promise<any> {
    return this.request<any>(`/api/v1/weather/historical?limit=${limit}`);
  }
  }

  // News
  async getNews(): Promise<NewsItem[]> {
    return this.request<NewsItem[]>('/api/v1/news');
  }

  // Stats
  async getStats(): Promise<SystemStats> {
    return this.request<SystemStats>('/api/v1/stats');
  }

  // Citizen Advisory
  async getCitizenStatus(lat: number, lng: number, lang = 'en'): Promise<CitizenStatus> {
    return this.request<CitizenStatus>(`/api/v1/citizen/status?lat=${lat}&lng=${lng}&lang=${lang}`);
  }

  // Demo Controls
  async triggerDemo(nodeId: string | number, type: string): Promise<any> {
    return this.request('/api/v1/demo/trigger', {
      method: 'POST',
      body: JSON.stringify({ node_id: nodeId, type })
    });
  }

  async controlDemoNetwork(nodeId: string | number, action: 'cut' | 'restore'): Promise<any> {
    return this.request('/api/v1/demo/network', {
      method: 'POST',
      body: JSON.stringify({ node_id: nodeId, action })
    });
  }

  // WhatsApp Simulator
  async simulateSarpanchReply(verificationId: number, replyText: string): Promise<any> {
    return this.request(`/api/whatsapp/simulate-reply?verification_id=${verificationId}&reply_text=${encodeURIComponent(replyText)}`, {
      method: 'POST'
    });
  }
}

export const api = new ApiClient();
