import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export default function MapView({
  nodes = [],
  alerts = [],
  shelters = [],
  selectedNodeId,
  onSelectNode,
  fireVectors = []
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersLayerRef = useRef(null);
  const hazardsLayerRef = useRef(null);
  const sheltersLayerRef = useRef(null);

  // Initialize Leaflet Map with CartoDB Positron Light Tiles
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const defaultCenter = [30.0869, 78.2676]; // Rishikesh-Garhwal catchment
    const map = L.map(mapContainerRef.current, {
      center: defaultCenter,
      zoom: 12,
      zoomControl: false,
      attributionControl: false
    });

    // Esri Light Gray Canvas for clean, high-contrast, watermark-free modern GIS
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 16,
      attribution: 'Esri, HERE, Garmin'
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Layer Groups
    hazardsLayerRef.current = L.layerGroup().addTo(map);
    sheltersLayerRef.current = L.layerGroup().addTo(map);
    markersLayerRef.current = L.layerGroup().addTo(map);

    mapInstanceRef.current = map;
    setTimeout(() => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.invalidateSize();
      }
    }, 250);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Hazard Geofences & Fire Spread Cones
  useEffect(() => {
    if (!hazardsLayerRef.current) return;
    hazardsLayerRef.current.clearLayers();

    alerts.forEach((alert) => {
      if (!alert.is_active) return;

      const isEmergency = alert.severity === 'EMERGENCY';
      const color = isEmergency ? '#dc2626' : '#d97706';

      // Circular hazard perimeter with soft transparent fill
      const circle = L.circle([alert.latitude, alert.longitude], {
        radius: (alert.radius_km || 4.0) * 1000,
        color: color,
        fillColor: color,
        fillOpacity: 0.12,
        weight: isEmergency ? 2 : 1.5,
        dashArray: isEmergency ? null : '4, 6'
      });

      circle.bindTooltip(
        `<b>${alert.hazard_type.toUpperCase()} ALERT: ${alert.title}</b><br/>Radius: ${alert.radius_km}km | Severity: ${alert.severity}`,
        { sticky: true }
      );
      hazardsLayerRef.current.addLayer(circle);
    });

    // Render Wildfire Cones
    fireVectors.forEach((vector) => {
      if (vector && vector.cone_polygon_coords && vector.cone_polygon_coords.length > 2) {
        const polygon = L.polygon(vector.cone_polygon_coords, {
          color: '#ea580c',
          fillColor: '#ea580c',
          fillOpacity: 0.18,
          weight: 2,
          dashArray: '4, 4'
        });
        polygon.bindTooltip(
          `<b>Wildfire Spread Projection Cone</b><br/>Speed: ${vector.propagation_speed_kmh} km/h | Bearing: ${vector.bearing_degrees}°`,
          { sticky: true }
        );
        hazardsLayerRef.current.addLayer(polygon);
      }
    });
  }, [alerts, fireVectors]);

  // Update Safe Evacuation Shelters
  useEffect(() => {
    if (!sheltersLayerRef.current) return;
    sheltersLayerRef.current.clearLayers();

    shelters.forEach((shelter) => {
      const shelterIcon = L.divIcon({
        className: 'custom-shelter-marker',
        html: `
          <div style="
            width: 26px; height: 26px;
            background: #ffffff;
            border: 2px solid #16a34a;
            border-radius: 6px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 6px rgba(22, 163, 74, 0.25);
            cursor: pointer;
            font-size: 13px;
          ">
            🏥
          </div>
        `,
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      });

      const marker = L.marker([shelter.latitude, shelter.longitude], { icon: shelterIcon });
      marker.bindPopup(`
        <div style="padding: 6px 4px; min-width: 170px;">
          <h4 style="color: #16a34a; margin: 0 0 4px 0; font-size: 0.9rem; font-weight: 700;">${shelter.name}</h4>
          <p style="margin: 0; font-size: 0.78rem; color: #475569;">Type: <b style="color:#0f172a;">${shelter.shelter_type}</b></p>
          <p style="margin: 2px 0; font-size: 0.78rem; color: #475569;">Capacity: <b style="color:#0f172a;">${shelter.capacity}</b> persons</p>
          <p style="margin: 2px 0; font-size: 0.78rem; color: #475569;">Helpline: <b style="color:#0f172a;">${shelter.contact_number}</b></p>
        </div>
      `);
      sheltersLayerRef.current.addLayer(marker);
    });
  }, [shelters]);

  // Update Sensor Nodes
  useEffect(() => {
    if (!markersLayerRef.current) return;
    markersLayerRef.current.clearLayers();

    nodes.forEach((node) => {
      const isSelected = node.id === selectedNodeId;
      const isGateway = node.is_gateway;
      const isBlackoutOffline = node.status === 'OFFLINE_CELLULAR';
      const nodeStatus = node.status || 'ONLINE';
      const hazardType = (node.hazard_type || 'multi').toLowerCase();

      // Node color by hazard type
      let baseColor = '#0284c7';
      let iconSymbol = '📡';

      if (isGateway) {
        baseColor = isBlackoutOffline ? '#dc2626' : '#0284c7';
        iconSymbol = isBlackoutOffline ? '⚡' : '🌐';
      } else if (hazardType === 'flood') {
        baseColor = '#2563eb';
        iconSymbol = '🌊';
      } else if (hazardType === 'fire') {
        baseColor = '#ea580c';
        iconSymbol = '🔥';
      } else if (hazardType === 'pollution') {
        baseColor = '#7c3aed';
        iconSymbol = '🌫️';
      }

      const ringStyle = isSelected ? 'box-shadow: 0 0 0 3px #0284c7, 0 4px 12px rgba(2, 132, 199, 0.3); transform: scale(1.1);' : 'box-shadow: 0 2px 5px rgba(0,0,0,0.12);';
      const batteryDisplay = node.battery_pct != null ? Number(node.battery_pct).toFixed(0) : '95';
      const rssiDisplay = node.signal_rssi != null ? node.signal_rssi : -65;
      const hopsDisplay = node.hop_count && node.hop_count > 0 ? `(${node.hop_count}h)` : '';

      const nodeIcon = L.divIcon({
        className: 'custom-node-marker',
        html: `
          <div style="
            width: ${isSelected ? '32px' : '28px'};
            height: ${isSelected ? '32px' : '28px'};
            background: #ffffff;
            border: 2px solid ${baseColor};
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.15s ease;
            position: relative;
            ${ringStyle}
          ">
            ${iconSymbol}
            <span style="
              position: absolute;
              bottom: -17px;
              font-size: 9px;
              font-weight: 700;
              background: #ffffff;
              padding: 1px 4px;
              border-radius: 4px;
              border: 1px solid #cbd5e1;
              color: #0f172a;
              white-space: nowrap;
              box-shadow: 0 1px 2px rgba(0,0,0,0.06);
            ">
              ${node.id} ${hopsDisplay}
            </span>
          </div>
        `,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });

      const marker = L.marker([node.latitude || 30.0869, node.longitude || 78.2676], { icon: nodeIcon });

      marker.on('click', () => {
        if (onSelectNode) onSelectNode(node.id);
      });

      marker.bindPopup(`
        <div style="padding: 6px 4px; min-width: 180px;">
          <h4 style="color: ${baseColor}; margin: 0 0 4px 0; font-size: 0.9rem; font-weight: 700;">${node.name}</h4>
          <div style="font-size: 0.78rem; color: #475569; line-height: 1.5;">
            <div>ID: <b style="color:#0f172a;">${node.id}</b></div>
            <div>Status: <b style="color:${nodeStatus.includes('OFFLINE') ? '#dc2626' : '#16a34a'};">${nodeStatus}</b></div>
            <div>Mesh Hops: <b>${node.hop_count || 0}</b> (Parent: ${node.parent_node_id || 'Direct'})</div>
            <div>Battery: <b>${batteryDisplay}%</b> | RSSI: <b>${rssiDisplay} dBm</b></div>
          </div>
        </div>
      `);

      markersLayerRef.current.addLayer(marker);
    });
  }, [nodes, selectedNodeId, onSelectNode]);

  const handleResetCenter = () => {
    if (mapInstanceRef.current) {
      mapInstanceRef.current.flyTo([30.0869, 78.2676], 12, { duration: 1.2 });
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <div ref={mapContainerRef} className="map-element" />

      {/* Floating Map Legend (Clean White) */}
      <div style={{
        position: 'absolute',
        top: 14,
        left: 14,
        background: 'rgba(255, 255, 255, 0.94)',
        backdropFilter: 'blur(8px)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '10px 14px',
        fontSize: '0.74rem',
        color: 'var(--text-secondary)',
        zIndex: 500,
        boxShadow: 'var(--shadow-md)',
        display: 'flex',
        flexDirection: 'column',
        gap: '5px'
      }}>
        <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2, fontSize: '0.78rem' }}>
          GIS Threat & Node Layer
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#0284c7' }} />
          <span>Gateway Sink (GSM/LoRa)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#2563eb' }} />
          <span>River Flood Gauge</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#ea580c' }} />
          <span>Wildfire Ridge Sensor</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#7c3aed' }} />
          <span>AQI Smog Sentry</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '2px', background: '#16a34a' }} />
          <span>Safe Evacuation Shelter</span>
        </div>
      </div>

      {/* Reset Center Button */}
      <button
        onClick={handleResetCenter}
        style={{
          position: 'absolute',
          top: 14,
          right: 14,
          background: '#ffffff',
          color: '#0f172a',
          border: '1px solid var(--border-medium)',
          borderRadius: 'var(--radius-md)',
          padding: '6px 12px',
          fontSize: '0.75rem',
          fontWeight: 600,
          cursor: 'pointer',
          zIndex: 500,
          boxShadow: 'var(--shadow-subtle)'
        }}
      >
        🎯 Reset View
      </button>
    </div>
  );
}
