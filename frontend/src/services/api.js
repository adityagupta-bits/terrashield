const API_BASE = typeof window !== 'undefined' && window.location.origin
  ? `${window.location.origin}/api`
  : "http://127.0.0.1:8000/api";

export async function fetchNodes() {
  const res = await fetch(`${API_BASE}/nodes`);
  if (!res.ok) throw new Error("Failed to fetch nodes");
  return res.json();
}

export async function fetchMeshTopology() {
  const res = await fetch(`${API_BASE}/nodes/topology`);
  if (!res.ok) throw new Error("Failed to fetch mesh topology");
  return res.json();
}

export async function toggleCellularBlackout(active) {
  const res = await fetch(`${API_BASE}/nodes/blackout?active=${active}`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to toggle blackout");
  return res.json();
}

export async function fetchLatestTelemetry() {
  const res = await fetch(`${API_BASE}/telemetry/latest`);
  if (!res.ok) throw new Error("Failed to fetch latest telemetry");
  return res.json();
}

export async function fetchNodeHistory(nodeId, limit = 25) {
  const res = await fetch(`${API_BASE}/telemetry/history/${nodeId}?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch node history");
  return res.json();
}

export async function fetchAIForecast(nodeId) {
  const res = await fetch(`${API_BASE}/telemetry/ai-forecast/${nodeId}`);
  if (!res.ok) throw new Error("Failed to fetch AI forecast");
  return res.json();
}

export async function fetchAlerts(activeOnly = false) {
  const res = await fetch(`${API_BASE}/alerts?active_only=${activeOnly}`);
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

export async function executeAlertAction(alertId, action) {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action })
  });
  if (!res.ok) throw new Error("Failed to execute alert action");
  return res.json();
}

export async function fetchSafeShelters() {
  const res = await fetch(`${API_BASE}/alerts/shelters`);
  if (!res.ok) throw new Error("Failed to fetch shelters");
  return res.json();
}

export async function checkCitizenLocation(lat, lon) {
  const res = await fetch(`${API_BASE}/alerts/citizen-check?lat=${lat}&lon=${lon}`);
  if (!res.ok) throw new Error("Failed to check citizen risk");
  return res.json();
}

export async function fetchWhatsAppVerifications(incidentId = null) {
  const url = incidentId 
    ? `${API_BASE}/whatsapp/verifications?incident_id=${incidentId}`
    : `${API_BASE}/whatsapp/verifications`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch verifications");
  return res.json();
}

export async function simulateSarpanchReply(verificationId, replyText) {
  const res = await fetch(`${API_BASE}/whatsapp/simulate-reply?verification_id=${verificationId}&reply_text=${encodeURIComponent(replyText)}`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to simulate Sarpanch reply");
  return res.json();
}

export async function triggerSimulationScenario(scenario, targetNodeId = null) {
  const res = await fetch(`${API_BASE}/simulation/trigger`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario, target_node_id: targetNodeId })
  });
  if (!res.ok) throw new Error("Failed to trigger simulation scenario");
  return res.json();
}
