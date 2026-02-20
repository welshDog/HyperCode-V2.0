import { ProjectPlan, Phase, Task } from '../components/plan/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_CORE_URL || 'http://localhost:8000';

class PlanService {
  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        // Try to parse error message
        let errorMessage = response.statusText;
        try {
            const errorBody = await response.json();
            errorMessage = errorBody.detail || errorBody.message || errorMessage;
        } catch (e) {
            // ignore JSON parse error
        }
        throw new Error(`API Error (${response.status}): ${errorMessage}`);
      }

      return response.json();
    } catch (error) {
        console.error(`Fetch error for ${url}:`, error);
        throw error;
    }
  }

  async listPlans(): Promise<ProjectPlan[]> {
    try {
        return await this.fetch<ProjectPlan[]>('/plans');
    } catch (error) {
        console.warn('Failed to fetch plans from API, falling back to mock data', error);
        return Promise.resolve(MOCK_PLANS);
    }
  }

  async getPlan(id: string): Promise<ProjectPlan> {
    try {
        return await this.fetch<ProjectPlan>(`/plans/${id}`);
    } catch (error) {
        console.warn(`Failed to fetch plan ${id}, falling back to mock`, error);
        const plan = MOCK_PLANS.find(p => p.id === id);
        if (plan) return Promise.resolve(plan);
        throw error; // Propagate error if not found in mock
    }
  }

  async createPlan(plan: Omit<ProjectPlan, 'id' | 'createdAt' | 'updatedAt' | 'version'>): Promise<ProjectPlan> {
    return this.fetch<ProjectPlan>('/plans', {
      method: 'POST',
      body: JSON.stringify(plan),
    });
  }

  async updatePlan(id: string, plan: Partial<ProjectPlan>): Promise<ProjectPlan> {
    return this.fetch<ProjectPlan>(`/plans/${id}`, {
      method: 'PUT',
      body: JSON.stringify(plan),
    });
  }
  
  async updateTaskStatus(planId: string, phaseId: string, taskId: string, status: Task['status']): Promise<void> {
      // Optimistic update support handled by hook, this is just the API call
      return this.fetch<void>(`/plans/${planId}/phases/${phaseId}/tasks/${taskId}/status`, {
          method: 'PATCH',
          body: JSON.stringify({ status })
      });
  }
}

export const planService = new PlanService();

// Mock Data for Fallback/Demo
const MOCK_PLANS: ProjectPlan[] = [
    {
      id: 'demo-plan-1',
      title: 'Interactive Plan Mode Demo',
      description: 'A demonstration plan for testing the PlanViewer component.',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: 1,
      userId: 'user-1',
      isPublic: true,
      phases: [
        {
          id: 'phase-1',
          title: 'Phase 1: Foundation',
          status: 'completed',
          estimatedTime: '2 days',
          order: 0,
          description: 'Setup basic infrastructure and core services.',
          tasks: [
            { id: 't1', description: 'Initialize repository', status: 'completed', duration: '1h', order: 0 },
            { id: 't2', description: 'Configure Docker environment', status: 'completed', duration: '2h', order: 1 },
            { id: 't3', description: 'Setup CI/CD pipeline', status: 'completed', assignedAgent: 'devops-bot', order: 2 }
          ]
        },
        {
          id: 'phase-2',
          title: 'Phase 2: Interactive Features',
          status: 'in_progress',
          estimatedTime: '3 days',
          order: 1,
          description: 'Implement user-facing interactive components.',
          tasks: [
            { id: 't4', description: 'Create PlanViewer component', status: 'completed', assignedAgent: 'frontend-dev', order: 0 },
            { id: 't5', description: 'Add unit tests for PlanViewer', status: 'completed', duration: '4h', order: 1 },
            { id: 't6', description: 'Implement PlanEditor', status: 'pending', duration: '6h', order: 2 },
            { id: 't7', description: 'Integrate with backend API', status: 'pending', order: 3 }
          ]
        },
        {
          id: 'phase-3',
          title: 'Phase 3: Optimization',
          status: 'pending',
          estimatedTime: '1 week',
          order: 2,
          description: 'Optimize performance and add advanced features.',
          tasks: [
            { id: 't8', description: 'Code splitting', status: 'pending', order: 0 },
            { id: 't9', description: 'Performance monitoring', status: 'pending', order: 1 }
          ]
        }
      ]
    }
];
