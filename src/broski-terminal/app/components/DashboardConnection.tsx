
'use client';

import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { setDashboardData, setSwarmStatus, setConnectionStatus } from '../store/slices/dashboardSlice';
import { useWebSocket } from '../hooks/useWebSocket';
import { useSwarmData } from '../hooks/useSwarmData';

export const DashboardConnection = () => {
  const dispatch = useDispatch();
  const { data, isConnected } = useWebSocket('/dashboard/ws');
  
  // Activate Swarm Data Polling
  useSwarmData();

  useEffect(() => {
    dispatch(setConnectionStatus(isConnected));
    if (data && data.payload) {
      dispatch(setDashboardData(data.payload));
    }
  }, [data, isConnected, dispatch]);

  return null; // Logic only component
};
