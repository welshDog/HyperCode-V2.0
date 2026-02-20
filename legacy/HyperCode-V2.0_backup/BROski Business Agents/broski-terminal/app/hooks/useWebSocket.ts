import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebSocket(url: string) {
  const [data, setData] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    try {
      // Handle relative URLs if needed, but here we expect full URL or path
      // If path starts with /, prepend window.location.host
      let fullUrl = url;
      if (url.startsWith('/')) {
        // Assume backend is on port 8000 for local dev if not proxied
        // But in production setup (docker), Next.js might proxy.
        // Let's assume the user configures NEXT_PUBLIC_CORE_URL
        const coreUrl = process.env.NEXT_PUBLIC_CORE_URL || 'http://localhost:8000';
        fullUrl = coreUrl.replace('http', 'ws') + url;
      }

      const socket = new WebSocket(fullUrl);

      socket.onopen = () => {
        setIsConnected(true);
        setError(null);
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

      socket.onclose = () => {
        setIsConnected(false);
        // Reconnect after 3s
        reconnectTimeout.current = setTimeout(connect, 3000);
      };

      socket.onerror = (e) => {
        console.error('WebSocket error', e);
        setError('Connection error');
        socket.close();
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

  return { data, isConnected, error };
}
