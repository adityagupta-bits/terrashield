import { useEffect, useState, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';

export type ConnectionStatus = 'LIVE' | 'RECONNECTING' | 'MESH-OFFLINE';

export function useWebSocket() {
  const [status, setStatus] = useState<ConnectionStatus>('RECONNECTING');
  const queryClient = useQueryClient();
  const socketRef = useRef<WebSocket | null>(null);
  const retryCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<any>(null);

  useEffect(() => {
    let isMounted = true;

    const connect = () => {
      if (socketRef.current) {
        try {
          socketRef.current.close();
        } catch (e) {}
      }

      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const defaultWsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/live`;
      const wsUrl = import.meta.env.VITE_WS_URL || defaultWsUrl;

      try {
        const ws = new WebSocket(wsUrl);
        socketRef.current = ws;

        ws.onopen = () => {
          if (!isMounted) return;
          setStatus('LIVE');
          retryCountRef.current = 0;
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data = JSON.parse(event.data);
            handleIncomingEvent(data);
          } catch (e) {
            console.error('Error parsing WebSocket message:', e);
          }
        };

        ws.onclose = () => {
          if (!isMounted) return;
          retryCountRef.current += 1;
          if (retryCountRef.current > 5) {
            setStatus('MESH-OFFLINE');
          } else {
            setStatus('RECONNECTING');
          }

          // Exponential backoff reconnect
          const delay = Math.min(1000 * Math.pow(1.5, retryCountRef.current), 15000);
          reconnectTimeoutRef.current = setTimeout(connect, delay);
        };

        ws.onerror = () => {
          if (socketRef.current) {
            socketRef.current.close();
          }
        };
      } catch (e) {
        setStatus('MESH-OFFLINE');
        reconnectTimeoutRef.current = setTimeout(connect, 5000);
      }
    };

    const handleIncomingEvent = (event: { type: string; payload?: any; data?: any }) => {
      const payload = event.payload || event.data;
      const type = event.type.toLowerCase();

      if (type === 'alert' || type === 'incident_alert') {
        queryClient.invalidateQueries({ queryKey: ['alerts'] });
        queryClient.invalidateQueries({ queryKey: ['stats'] });
        queryClient.invalidateQueries({ queryKey: ['nodes'] });
      } else if (type === 'reading' || type === 'telemetry_update') {
        queryClient.invalidateQueries({ queryKey: ['nodes'] });
        if (payload?.node_id || payload?.node_code) {
          queryClient.invalidateQueries({ queryKey: ['readings', payload.node_id || payload.node_code] });
        }
      } else if (type === 'node_status') {
        queryClient.invalidateQueries({ queryKey: ['nodes'] });
        queryClient.invalidateQueries({ queryKey: ['stats'] });
      } else if (type === 'mesh_change' || type === 'network_state_change') {
        queryClient.invalidateQueries({ queryKey: ['mesh_topology'] });
        queryClient.invalidateQueries({ queryKey: ['nodes'] });
      } else if (type === 'whatsapp_message' || type === 'whatsapp_verification_update') {
        queryClient.invalidateQueries({ queryKey: ['alerts'] });
        queryClient.invalidateQueries({ queryKey: ['stats'] });
      } else if (type === 'alert_status_changed') {
        queryClient.invalidateQueries({ queryKey: ['alerts'] });
        queryClient.invalidateQueries({ queryKey: ['stats'] });
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [queryClient]);

  return { status };
}
