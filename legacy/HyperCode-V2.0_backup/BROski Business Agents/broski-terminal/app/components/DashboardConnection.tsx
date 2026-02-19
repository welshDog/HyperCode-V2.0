
'use client';

import { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { setDashboardData, setConnectionStatus } from '../store/slices/dashboardSlice';
import { useWebSocket } from '../hooks/useWebSocket';

export const DashboardConnection = () => {
  const dispatch = useDispatch();
  const { data, isConnected } = useWebSocket('/dashboard/ws');

  useEffect(() => {
    dispatch(setConnectionStatus(isConnected));
    if (data) {
      dispatch(setDashboardData(data));
    }
  }, [data, isConnected, dispatch]);

  return null; // Logic only component
};
