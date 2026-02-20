import { useState, useEffect, useRef, useCallback } from 'react';

export interface BridgeMessage {
  type: string;
  payload?: any;
  timestamp?: string;
  sender?: string;
}

export function useWebSocket(url: string) {
  const [data, setData] = useState<BridgeMessage | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryCount = useRef(0);
  const maxRetries = 10;

  const connect = useCallback(() => {
    try {
      // Handle relative URLs if needed, but here we expect full URL or path
      // If path starts with /, prepend window.location.host or configured backend
      let fullUrl = url;
      if (url.startsWith('/')) {
        // Assume backend is on port 8001 for Bridge Server local dev
        // In docker, this might be mapped differently.
        // For now, default to localhost:8001/ws/bridge if not configured
        const bridgeUrl = process.env.NEXT_PUBLIC_BRIDGE_URL || 'ws://localhost:8001';
        fullUrl = `${bridgeUrl}${url}`;
      }

      console.log(`Connecting to WebSocket: ${fullUrl}`);
      const socket = new WebSocket(fullUrl);

      socket.onopen = () => {
        setIsConnected(true);
        setError(null);
        retryCount.current = 0; // Reset retries on success
        console.log('WebSocket connected');
      };

      socket.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setData(parsed);
        } catch (e) {
          console.error('Failed to parse WebSocket message', e);
        }
      };

      socket.onclose = (event) => {
        setIsConnected(false);
        console.log(`WebSocket disconnected: Code ${event.code}`);
        
        // Exponential backoff for reconnection
        const delay = Math.min(1000 * Math.pow(2, retryCount.current), 30000);
        
        if (retryCount.current < maxRetries) {
            console.log(`Reconnecting in ${delay}ms... (Attempt ${retryCount.current + 1}/${maxRetries})`);
            reconnectTimeout.current = setTimeout(() => {
                retryCount.current += 1;
                connect();
            }, delay);
        } else {
            setError('Max reconnection attempts reached');
        }
      };

      socket.onerror = (e) => {
        console.error('WebSocket error', e);
        // Don't set hard error state here, let onclose handle reconnection logic
      };

      ws.current = socket;
    } catch (e) {
      console.error('WebSocket connection failed', e);
      setError('Failed to connect');
    }
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [connect]);

  // Helper to send messages
  const sendMessage = useCallback((message: any) => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify(message));
      } else {
          console.warn("WebSocket not connected, cannot send message");
      }
  }, []);

  return { data, isConnected, error, sendMessage };
}

