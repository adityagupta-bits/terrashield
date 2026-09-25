class WebSocketClient {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.reconnectTimer = null;
    this.isConnected = false;
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = typeof window !== 'undefined' && window.location.host
      ? `${protocol}//${window.location.host}/ws/live`
      : "ws://127.0.0.1:8000/ws/live";
    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        console.log("Connected to TERRA SHIELD Live WebSocket");
        this.isConnected = true;
        this.emit("CONNECTION_STATUS", { connected: true });
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type && payload.data) {
            this.emit(payload.type, payload.data);
          }
        } catch (e) {
          // Heartbeat or raw string
        }
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.emit("CONNECTION_STATUS", { connected: false });
        this.scheduleReconnect();
      };

      this.socket.onerror = (err) => {
        console.warn("WebSocket error:", err);
        this.socket.close();
      };
    } catch (err) {
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (!this.reconnectTimer) {
      this.reconnectTimer = setTimeout(() => {
        this.reconnectTimer = null;
        this.connect();
      }, 3000);
    }
  }

  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);

    // Return unsubscribe function
    return () => {
      if (this.listeners.has(eventType)) {
        this.listeners.get(eventType).delete(callback);
      }
    };
  }

  emit(eventType, data) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).forEach((cb) => {
        try {
          cb(data);
        } catch (e) {
          console.error("Error in WS listener:", e);
        }
      });
    }
  }
}

export const wsClient = new WebSocketClient();
