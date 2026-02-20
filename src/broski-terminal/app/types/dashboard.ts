
export interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'idle' | 'busy' | 'offline' | 'error';
  version: string;
  capabilities: string[];
  load: number;
  lastHeartbeat: string;
}

export interface Mission {
  id: string;
  title: string;
  status: 'queued' | 'assigned' | 'in_progress' | 'completed' | 'failed';
  priority: number;
  agentId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface MemoryStats {
  total_memories: number;
  last_updated: number;
}

export interface DashboardState {
  agents: Agent[];
  missions: Mission[];
  memory: MemoryStats;
  memoryHistory: { timestamp: number; count: number }[];
  system_status: string;
  phase: string;
  activeCrew: string[];
  last_update: number;
  connected: boolean;
}
