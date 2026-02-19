
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { DashboardState, Agent, Mission, MemoryStats } from '../../types/dashboard';

const initialState: DashboardState = {
  agents: [],
  missions: [],
  memory: {
    total_memories: 0,
    last_updated: 0
  },
  memoryHistory: [],
  system_status: 'unknown',
  phase: 'unknown' as any,
  activeCrew: [],
  last_update: 0,
  connected: false
};

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setDashboardData(state, action: PayloadAction<{
      agents: Agent[];
      missions: Mission[];
      memory: MemoryStats;
      system_status: string;
      phase?: string;
      activeCrew?: string[];
      timestamp: number;
    }>) {
      state.agents = action.payload.agents;
      state.missions = action.payload.missions;
      state.memory = action.payload.memory;
      state.system_status = action.payload.system_status;
      if (action.payload.phase) state.phase = action.payload.phase;
      if (action.payload.activeCrew) state.activeCrew = action.payload.activeCrew;
      state.last_update = action.payload.timestamp;
      state.connected = true;

      // Add to history
      const lastPoint = state.memoryHistory[state.memoryHistory.length - 1];
      if (!lastPoint || lastPoint.count !== action.payload.memory.total_memories || (action.payload.timestamp - lastPoint.timestamp > 30)) {
        state.memoryHistory.push({
          timestamp: action.payload.timestamp,
          count: action.payload.memory.total_memories
        });
        if (state.memoryHistory.length > 50) {
          state.memoryHistory.shift();
        }
      }
    },
    setSwarmStatus(state, action: PayloadAction<{ phase: string; activeCrew: string[] }>) {
      state.phase = action.payload.phase;
      state.activeCrew = action.payload.activeCrew;
    },
    setConnectionStatus(state, action: PayloadAction<boolean>) {
      state.connected = action.payload;
    }
  }
});

export const { setDashboardData, setSwarmStatus, setConnectionStatus } = dashboardSlice.actions;
export default dashboardSlice.reducer;
