import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { NodeItem, AlertItem } from '../../types';

interface MapViewProps {
  nodes: NodeItem[];
  alerts?: AlertItem[];
  selectedNodeId?: string;
  onSelectNode: (nodeCode: string) => void;
  zonesGeoJson?: any;
  shelters?: any[];
  center?: [number, number];
  zoom?: number;
}

export const MapView: React.FC<MapViewProps> = ({
  nodes,
  alerts = [],
  selectedNodeId,
  onSelectNode,
  zonesGeoJson,
  shelters = [],
  center = [26.1850, 91.7500],
  zoom = 11
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const zonesLayerRef = useRef<L.GeoJSON | null>(null);
  const sheltersLayerRef = useRef<L.LayerGroup | null>(null);

  // Initialize map once
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center,
      zoom,
      zoomControl: false,
      attributionControl: false
    });

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // High-contrast tactical CartoDB Dark Matter tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(map);

    markersLayerRef.current = L.layerGroup().addTo(map);
    sheltersLayerRef.current = L.layerGroup().addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update center when prop changes
  useEffect(() => {
    if (mapInstanceRef.current && center) {
      mapInstanceRef.current.setView(center, zoom, { animate: true });
    }
  }, [center, zoom]);

  // Update Hazard Zones
  useEffect(() => {
    if (!mapInstanceRef.current || !zonesGeoJson) return;

    if (zonesLayerRef.current) {
      mapInstanceRef.current.removeLayer(zonesLayerRef.current);
    }

    try {
      zonesLayerRef.current = L.geoJSON(zonesGeoJson, {
        style: (feature) => {
          const risk = feature?.properties?.risk_level || 'medium';
          let color = '#3b82f6';
          let fillColor = '#3b82f6';
          if (risk === 'critical') {
            color = '#dc2626';
            fillColor = '#dc2626';
          } else if (risk === 'high') {
            color = '#f59e0b';
            fillColor = '#f59e0b';
          }
          return {
            color,
            weight: 2,
            opacity: 0.8,
            fillColor,
            fillOpacity: 0.18,
            dashArray: '4, 4'
          };
        },
        onEachFeature: (feature, layer) => {
          layer.bindTooltip(`<b>${feature.properties.name}</b><br/>Risk Level: ${feature.properties.risk_level.toUpperCase()}`, {
            direction: 'top',
            className: 'custom-leaflet-tooltip'
          });
        }
      }).addTo(mapInstanceRef.current);
    } catch (e) {
      console.error('Error rendering hazard zones:', e);
    }
  }, [zonesGeoJson]);

  // Update Shelters
  useEffect(() => {
    if (!sheltersLayerRef.current || !shelters.length) return;
    sheltersLayerRef.current.clearLayers();

    shelters.forEach((s) => {
      const icon = L.divIcon({
        className: 'custom-shelter-marker',
        html: `
          <div style="
            background: #0284c7;
            width: 26px;
            height: 26px;
            border-radius: 6px;
            border: 2px solid #38bdf8;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 13px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
          ">
            🏠
          </div>
        `,
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      });

      const marker = L.marker([s.latitude, s.longitude], { icon });
      marker.bindPopup(`
        <div style="font-family: sans-serif; min-width: 170px;">
          <h4 style="font-weight: 700; margin: 0 0 4px 0; color: #0f172a; font-size: 13px;">${s.name}</h4>
          <p style="margin: 0 0 4px 0; font-size: 11px; color: #475569;"><b>Type:</b> Safe Relief Shelter</p>
          <p style="margin: 0 0 4px 0; font-size: 11px; color: #475569;"><b>Capacity:</b> ${s.capacity || 500} | <b>Occupancy:</b> ${s.occupancy || 15}</p>
          <p style="margin: 0; font-size: 11px; color: #0284c7;"><b>Phone:</b> ${s.phone || '112'}</p>
        </div>
      `);
      sheltersLayerRef.current?.addLayer(marker);
    });
  }, [shelters]);

  // Update Node Markers
  useEffect(() => {
    if (!markersLayerRef.current) return;
    markersLayerRef.current.clearLayers();

    nodes.forEach((node) => {
      const isSelected = selectedNodeId === node.code || selectedNodeId === String(node.id);
      const isCritical = node.status === 'critical';
      const isWarning = node.status === 'warning';
      const isOffline = node.status === 'offline';
      const isHardware = !node.is_simulated;

      let color = '#16a34a'; // normal green
      if (isCritical) color = '#dc2626';
      else if (isWarning) color = '#f59e0b';
      else if (isOffline) color = '#6b7280';

      const pulseRingHtml = isCritical
        ? `<div style="
            position: absolute;
            top: -6px;
            left: -6px;
            width: ${isHardware ? '36px' : '30px'};
            height: ${isHardware ? '36px' : '30px'};
            border-radius: 50%;
            border: 2px solid #dc2626;
            animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
          "></div>`
        : '';

      const badgeHtml = isHardware
        ? `<span style="
            position: absolute;
            bottom: -6px;
            left: 50%;
            transform: translateX(-50%);
            background: #2563eb;
            color: #ffffff;
            font-size: 8px;
            font-weight: 800;
            padding: 1px 3px;
            border-radius: 3px;
            letter-spacing: 0.5px;
            white-space: nowrap;
            border: 1px solid #60a5fa;
          ">PHY</span>`
        : '';

      const markerHtml = `
        <div style="position: relative; width: 100%; height: 100%; cursor: pointer;">
          ${pulseRingHtml}
          <div style="
            background: ${color};
            width: ${isHardware ? '24px' : '18px'};
            height: ${isHardware ? '24px' : '18px'};
            border-radius: 50%;
            border: ${isSelected ? '3px solid #ffffff' : '2px solid rgba(255,255,255,0.85)'};
            box-shadow: 0 0 10px ${color}88;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 9px;
            margin: auto;
          ">
            ${node.is_gateway ? '★' : ''}
          </div>
          ${badgeHtml}
        </div>
      `;

      const icon = L.divIcon({
        className: 'custom-node-icon',
        html: markerHtml,
        iconSize: [isHardware ? 26 : 20, isHardware ? 26 : 20],
        iconAnchor: [isHardware ? 13 : 10, isHardware ? 13 : 10]
      });

      const marker = L.marker([node.latitude, node.longitude], { icon });

      marker.on('click', () => {
        onSelectNode(node.code);
      });

      marker.bindTooltip(`
        <div style="font-family: sans-serif; font-size: 11px;">
          <b style="color: #f8fafc;">${node.code}</b>: ${node.name}<br/>
          <span style="color: ${color}; text-transform: uppercase; font-weight: 700;">Status: ${node.status}</span>
          ${isHardware ? '<br/><span style="color: #60a5fa; font-weight: 600;">[Physical Hardware]</span>' : ''}
        </div>
      `, {
        direction: 'top',
        className: 'custom-leaflet-tooltip'
      });

      markersLayerRef.current?.addLayer(marker);
    });
  }, [nodes, selectedNodeId, onSelectNode]);

  return (
    <div className="w-full h-full relative">
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};
