import { AgentStatus } from '../stores/aiStore';

export interface AgentDto {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  logs?: string[];
}

export interface TaskDto {
  id: string;
  title: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high';
  progress: number;
}

export class HypercodeCoreClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = (import.meta as any).env.VITE_HYPERCODE_CORE_URL || 'http://localhost:8000';
    // In a real app, token would be managed by an AuthContext
    this.token = (import.meta as any).env.VITE_API_KEY || null;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token ? { 'X-API-Key': this.token } : {}),
      ...options.headers,
    };

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (!response.ok) {
        if (response.status === 401) {
          // Handle token refresh logic here
          console.warn('Unauthorized - Token refresh needed');
        }
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.message || `Request failed with status ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error(`API Request Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // --- Agent Methods ---

  async getAgents(): Promise<AgentDto[]> {
    return this.request<AgentDto[]>('/api/v1/agents');
  }

  async generateAgent(prompt: string): Promise<AgentDto> {
    return this.request<AgentDto>('/api/v1/ai/generate', {
      method: 'POST',
      body: JSON.stringify({ task_description: prompt }),
    });
  }

  async getBudgetStatus(): Promise<{ total: number; spent: number }> {
    return this.request<{ total: number; spent: number }>('/api/v1/ai/budget/status');
  }

  // --- WebSocket URL Helper ---
  
  getWebSocketUrl(): string {
    const wsProtocol = this.baseUrl.startsWith('https') ? 'wss' : 'ws';
    const wsBase = this.baseUrl.replace(/^https?:\/\//, '');
    return `${wsProtocol}://${wsBase}/dashboard/ws${this.token ? `?token=${this.token}` : ''}`;
  }

  getArtifactUrl(agentId: string): string {
    return `${this.baseUrl}/api/v1/agents/${agentId}/artifact`;
  }
}

export const hypercodeCoreClient = new HypercodeCoreClient();
