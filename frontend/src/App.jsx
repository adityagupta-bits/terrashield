import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MapView from './components/MapView';
import MeshTopologyView from './components/MeshTopologyView';
import TelemetryPanel from './components/TelemetryPanel';
import AlertCenter from './components/AlertCenter';
import WhatsAppBotModal from './components/WhatsAppBotModal';
import CitizenPortalModal from './components/CitizenPortalModal';
import CitizenView from './components/CitizenView';
import GovernmentFooter from './components/GovernmentFooter';

import {
  fetchNodes,
  fetchMeshTopology,
  fetchAlerts,
  fetchSafeShelters,
  fetchNodeHistory,
  fetchAIForecast,
  executeAlertAction,
  toggleCellularBlackout
} from './services/api';
import { wsClient } from './services/websocket';
import { Map, Share2 } from 'lucide-react';

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState('NODE-03');
  const [nodeHistory, setNodeHistory] = useState([]);
  const [aiForecast, setAiForecast] = useState(null);
  const [topology, setTopology] = useState({ nodes: [], links: [], network_mode: 'HYBRID_CELLULAR' });
  const [alerts, setAlerts] = useState([]);
  const [shelters, setShelters] = useState([]);
  const [activeTab, setActiveTab] = useState('MAP'); // 'MAP' | 'TOPOLOGY'
  const [wsConnected, setWsConnected] = useState(false);
  const [blackoutActive, setBlackoutActive] = useState(false);
  const initialView = (typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('view')?.toUpperCase() === 'USER') ? 'USER' : 'ADMIN';
  const [currentView, setCurrentView] = useState(initialView);

  // Modals
  const [showWhatsAppModal, setShowWhatsAppModal] = useState(false);
  const [targetIncidentId, setTargetIncidentId] = useState(null);
  const [showCitizenModal, setShowCitizenModal] = useState(false);

  // Initial Data Fetch
  useEffect(() => {
    loadInitialData();

    // Setup WebSocket
    wsClient.connect();
    
    const unsubs = [
      wsClient.on('CONNECTION_STATUS', (data) => setWsConnected(data.connected)),
      wsClient.on('TELEMETRY_UPDATE', handleLiveTelemetry),
      wsClient.on('INCIDENT_ALERT', handleNewAlert),
      wsClient.on('NETWORK_STATE_CHANGE', handleNetworkChange),
      wsClient.on('WHATSAPP_VERIFICATION_UPDATE', handleVerificationUpdate),
      wsClient.on('ALERT_STATUS_CHANGED', handleAlertStatusChange),
      wsClient.on('SIMULATION_RESET', loadInitialData)
    ];

    return () => {
      unsubs.forEach(fn => fn && fn());
    };
  }, []);

  // Fetch History and AI Forecast when selected node changes
  useEffect(() => {
    if (selectedNodeId) {
      loadNodeTelemetry(selectedNodeId);
    }
  }, [selectedNodeId]);

  const loadInitialData = async () => {
    try {
      const [nodesData, topoData, alertsData, sheltersData] = await Promise.all([
        fetchNodes(),
        fetchMeshTopology(),
        fetchAlerts(),
        fetchSafeShelters()
      ]);

      setNodes(nodesData);
      setTopology(topoData);
      setAlerts(alertsData);
      setShelters(sheltersData);
      setBlackoutActive(topoData.network_mode?.includes('BLACKOUT') || false);

      if (nodesData.length > 0 && !selectedNodeId) {
        setSelectedNodeId(nodesData[0].id);
      }
    } catch (e) {
      console.error('Error loading initial data:', e);
    }
  };

  const loadNodeTelemetry = async (nodeId) => {
    try {
      const [history, forecast] = await Promise.all([
        fetchNodeHistory(nodeId, 15),
        fetchAIForecast(nodeId)
      ]);
      setNodeHistory(history);
      setAiForecast(forecast);
    } catch (e) {
      console.error('Error loading node telemetry:', e);
    }
  };

  const handleLiveTelemetry = (telemetry) => {
    setNodes((prevNodes) =>
      prevNodes.map((n) => (n.id === telemetry.node_id ? { ...n, ...telemetry } : n))
    );

    // If matches currently selected node, append to chart
    if (telemetry.node_id === selectedNodeId) {
      setNodeHistory((prev) => [...prev.slice(-14), telemetry]);
      fetchAIForecast(selectedNodeId).then(setAiForecast).catch(() => {});
    }
  };

  const handleNewAlert = (alert) => {
    setAlerts((prev) => [alert, ...prev.filter(a => a.id !== alert.id)]);
  };

  const handleNetworkChange = (change) => {
    setBlackoutActive(change.cellular_blackout);
    fetchMeshTopology().then(setTopology).catch(() => {});
    fetchNodes().then(setNodes).catch(() => {});
  };

  const handleVerificationUpdate = (verif) => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === verif.incident_id
          ? { ...a, verified_by_human: verif.status === 'CONFIRMED' }
          : a
      )
    );
  };

  const handleAlertStatusChange = (status) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === status.alert_id ? { ...a, ...status } : a))
    );
  };

  const handleAlertAction = async (alertId, action) => {
    try {
      const updated = await executeAlertAction(alertId, action);
      setAlerts((prev) => prev.map(a => a.id === alertId ? updated : a));
    } catch (e) {
      console.error('Failed to execute alert action', e);
    }
  };

  const handleToggleBlackout = async () => {
    try {
      await toggleCellularBlackout(!blackoutActive);
    } catch (e) {
      console.error('Failed to toggle blackout', e);
    }
  };

  const handleScenarioTriggered = () => {
    loadInitialData();
    if (selectedNodeId) loadNodeTelemetry(selectedNodeId);
  };

  const selectedNode = nodes.find(n => n.id === selectedNodeId) || nodes[0];
  const activeAlertsCount = alerts.filter(a => a.is_active).length;
  const fireVectors = aiForecast?.fire_spread_vector ? [aiForecast.fire_spread_vector] : [];

  return (
    <div className={`app-container ${currentView === 'ADMIN' ? 'admin-theme' : 'user-theme'}`} style={{ height: 'auto', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Mission Control Bar & Government Warning Ticker */}
      <Navbar
        wsConnected={wsConnected}
        networkMode={topology.network_mode}
        activeAlertsCount={activeAlertsCount}
        onOpenWhatsApp={() => {
          setTargetIncidentId(null);
          setShowWhatsAppModal(true);
        }}
        onOpenCitizenPortal={() => setCurrentView('USER')}
        onToggleBlackout={handleToggleBlackout}
        blackoutActive={blackoutActive}
        onScenarioTriggered={handleScenarioTriggered}
        currentView={currentView}
        onToggleView={(view) => {
          setCurrentView(view);
          if (typeof window !== 'undefined') {
            window.history.replaceState(null, '', view === 'USER' ? '?view=user' : '/');
          }
        }}
      />

      {/* Main Workspace Layout: Admin vs Citizen Portal */}
      {currentView === 'ADMIN' ? (
        <main className="dashboard-layout" style={{ flex: '1 0 auto' }}>
          {/* Left Area: Visual Map / Topology Viewport (Full-bleed) */}
          <div className="viewport-pane">
            <div className="viewport-toolbar">
              <div className="tab-group">
                <button
                  className={`tab-btn ${activeTab === 'MAP' ? 'active' : ''}`}
                  onClick={() => setActiveTab('MAP')}
                >
                  <Map size={14} />
                  <span>GIS Incident & Threat Map</span>
                </button>

                <button
                  className={`tab-btn ${activeTab === 'TOPOLOGY' ? 'active' : ''}`}
                  onClick={() => setActiveTab('TOPOLOGY')}
                >
                  <Share2 size={14} />
                  <span>Mesh Network Topology</span>
                </button>
              </div>

              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                Region: <b style={{ color: '#0f172a' }}>Rishikesh-Garhwal Catchment</b> • 20 Distributed Nodes
              </div>
            </div>

            <div style={{ flex: 1, position: 'relative', overflow: 'hidden', minHeight: '640px' }}>
              {activeTab === 'MAP' ? (
                <MapView
                  nodes={nodes}
                  alerts={alerts}
                  shelters={shelters}
                  selectedNodeId={selectedNodeId}
                  onSelectNode={setSelectedNodeId}
                  fireVectors={fireVectors}
                />
              ) : (
                <MeshTopologyView
                  topology={topology}
                  selectedNodeId={selectedNodeId}
                  onSelectNode={setSelectedNodeId}
                  onToggleBlackout={handleToggleBlackout}
                />
              )}
            </div>
          </div>

          {/* Right Area: Integrated Sidebar (Cardless) */}
          <aside className="sidebar-pane">
            {/* Active Disaster Incidents */}
            <AlertCenter
              alerts={alerts}
              onExecuteAction={handleAlertAction}
              onOpenWhatsApp={(incidentId) => {
                setTargetIncidentId(incidentId);
                setShowWhatsAppModal(true);
              }}
            />

            {/* Selected Node Live Telemetry & AI Forecast */}
            <TelemetryPanel
              node={selectedNode}
              history={nodeHistory}
              aiForecast={aiForecast}
            />
          </aside>
        </main>
      ) : (
        <main style={{ flex: '1 0 auto', background: '#f8fafc' }}>
          <CitizenView
            alerts={alerts}
            shelters={shelters}
            onOpenWhatsApp={() => {
              setTargetIncidentId(null);
              setShowWhatsAppModal(true);
            }}
          />
        </main>
      )}

      {/* Official Government of India & NDMA Sachet Deep Black Footer */}
      <GovernmentFooter />

      {/* Interactive Modals */}
      <WhatsAppBotModal
        isOpen={showWhatsAppModal}
        onClose={() => setShowWhatsAppModal(false)}
        incidentId={targetIncidentId}
        onVerificationUpdated={() => {
          fetchAlerts().then(setAlerts).catch(() => {});
        }}
      />

      <CitizenPortalModal
        isOpen={showCitizenModal}
        onClose={() => setShowCitizenModal(false)}
      />
    </div>
  );
}
