import { useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { useAIStore, AgentStatus } from '../stores/aiStore';
import { hypercodeCoreClient } from '../services/hypercodeCoreClient';

export const useAgentUpdates = () => {
  const { updateAgentStatus, setConnected } = useAIStore();
  
  // In a real app, we might want to get the URL dynamically or pass a token
  const socketUrl = hypercodeCoreClient.getWebSocketUrl();

  const { lastJsonMessage, readyState } = useWebSocket(socketUrl, {
    shouldReconnect: (closeEvent) => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
    share: true,
  });

  useEffect(() => {
    setConnected(readyState === ReadyState.OPEN);
  }, [readyState, setConnected]);

  useEffect(() => {
    if (lastJsonMessage) {
      const message = lastJsonMessage as any;
      
      // Handle different message types
      if (message.type === 'agent:update' || message.type === 'agent:complete' || message.type === 'agent:error') {
        const { id, status } = message.payload;
        if (id && status) {
          updateAgentStatus(id, status as AgentStatus);
        }
      }
    }
  }, [lastJsonMessage, updateAgentStatus]);

  return {
    isConnected: readyState === ReadyState.OPEN,
  };
};
