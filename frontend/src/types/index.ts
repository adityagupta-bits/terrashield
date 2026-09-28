export type HazardType = 'flood' | 'fire' | 'air' | 'multi' | 'none';
export type NodeStatus = 'normal' | 'warning' | 'critical' | 'offline';
export type AlertSeverity = 'warning' | 'critical';
export type AlertStatus = 'open' | 'acknowledged' | 'resolved' | 'dispatched';
export type GroundTruthStatus = 'unverified' | 'confirmed' | 'denied';

export interface NodeItem {
  id: number;
  code: string;
  name: string;
  hazard_type: HazardType;
  latitude: number;
  longitude: number;
  status: NodeStatus;
  battery_pct: number;
  signal_strength: number;
  mesh_level: number;
  parent_node_id?: number | null;
  parent_code?: string | null;
  is_gateway: boolean;
  is_simulated: boolean;
  is_backup_sink?: boolean;
  last_seen: string;
  // Live reading telemetry fields when populated
  water_level_cm?: number;
  water_rate_cm_min?: number;
  pm25?: number;
  temperature_c?: number;
  humidity?: number;
  smoke_index?: number;
}

export interface ReadingItem {
  id: number;
  ts: string;
  water_level_cm?: number;
  water_rate_cm_min?: number;
  pm25?: number;
  pm10?: number;
  temperature_c?: number;
  humidity?: number;
  smoke_index?: number;
  raw_bytes?: number;
  tx_bytes?: number;
}

export interface AlertItem {
  id: number;
  node_id?: number;
  node_code?: string;
  hazard_type: HazardType;
  severity: AlertSeverity;
  confidence: number;
  message: string;
  decided_on_device: boolean;
  decision_ms: number;
  reason?: string;
  node_timestamp: string;
  received_at: string;
  delivered_after_outage: boolean;
  status: AlertStatus;
  ground_truth: GroundTruthStatus;
  latitude: number;
  longitude: number;
}

export interface ContactItem {
  id: number;
  name: string;
  category: 'authority' | 'rescue' | 'shelter' | 'ngo' | 'helpline';
  phone: string;
  district: string;
  capacity?: number;
  occupancy?: number;
  latitude: number;
  longitude: number;
  distance_km?: number;
}

export interface WeatherCurrent {
  region: string;
  temp_c: number;
  humidity: number;
  rainfall_mm: number;
  wind_kmh: number;
  risk_badge: 'Low' | 'Medium' | 'High';
  ts: string;
}

export interface WeatherForecastPoint {
  time: string;
  temp_c: number;
  rainfall_mm: number;
  risk_level: string;
  predicted: boolean;
}

export interface WeatherForecastData {
  region: string;
  points: WeatherForecastPoint[];
  note: string;
}

export interface RiskAssessmentDetails {
  risk_type: string;
  triggered: boolean;
  score: number;
  reasons: string[];
}

export interface DailyProjection {
  date: string;
  temp_max: number;
  temp_min: number;
  humidity: number;
  precipitation: number;
  pressure: number;
  wind_speed: number;
}

export interface MultiHazardRiskData {
  region: string;
  coordinates: { latitude: number; longitude: number };
  horizon_days: number;
  overall_severity: 'LOW' | 'ELEVATED' | 'CRITICAL';
  max_risk_score: number;
  triggered_hazards: string[];
  dates: string[];
  daily_projections: DailyProjection[];
  risks: {
    flood: RiskAssessmentDetails;
    drought: RiskAssessmentDetails;
    fire: RiskAssessmentDetails;
  };
  model_metadata?: any;
}


export interface NewsItem {
  id: number;
  region: string;
  title: string;
  summary: string;
  source: string;
  published_at: string;
}

export interface SystemStats {
  nodes_online: number;
  total_nodes: number;
  open_alerts: number;
  bytes_raw_local: number;
  bytes_transmitted: number;
  alerts_sent_whatsapp_today: number;
  last_alert_time?: string | null;
}

export interface MeshLink {
  id: number;
  source: string;
  target: string;
  rssi: number;
  link_type: 'esp_now' | 'lora' | 'cellular';
  active: boolean;
}

export interface MeshTopologyData {
  network_mode: string;
  cellular_blackout: boolean;
  active_gateways: number;
  total_mesh_hops: number;
  backup_sink_active: boolean;
  backup_sink_node: string;
  nodes: NodeItem[];
  links: MeshLink[];
}

export interface ShelterDetail {
  id: number;
  name: string;
  distance_km: number;
  capacity: number;
  occupancy: number;
  available_spots: number;
  phone: string;
}

export interface CitizenStatus {
  status: 'safe' | 'caution' | 'evacuate';
  severity: string;
  message: string;
  hazard_type: string;
  nearest_shelters: ShelterDetail[];
}

export interface UserProfile {
  email: string;
  role: 'authority' | 'viewer';
  token: string;
}
