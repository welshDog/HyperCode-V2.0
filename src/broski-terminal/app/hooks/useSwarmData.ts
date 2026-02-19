import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { setSwarmStatus } from '../store/slices/dashboardSlice';

const POLLING_INTERVAL = 5000; // 5 seconds
const RETRY_DELAY = 1000;
const MAX_RETRIES = 3;

export const useSwarmData = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    let retryCount = 0;

    const fetchData = async () => {
      try {
        // Fetch Swarm Status from Core/Orchestrator
        const baseUrl = process.env.NEXT_PUBLIC_AGENTS_URL || 'http://localhost:8000';
        const crewRes = await fetch(`${baseUrl}/crew`);
        
        if (!crewRes.ok) {
            throw new Error(`HTTP error! status: ${crewRes.status}`);
        }
        
        const crewData = await crewRes.json();

        dispatch(setSwarmStatus({
          phase: crewData.phase,
          activeCrew: crewData.agents
        }));
        
        retryCount = 0; // Reset retry count on success

      } catch (error) {
        console.error('Swarm data polling error:', error);
        
        if (retryCount < MAX_RETRIES) {
            retryCount++;
            const backoff = RETRY_DELAY * Math.pow(2, retryCount - 1);
            setTimeout(fetchData, backoff);
        }
      }
    };

    const interval = setInterval(fetchData, POLLING_INTERVAL);
    fetchData(); // Initial fetch

    return () => clearInterval(interval);
  }, [dispatch]);
};
