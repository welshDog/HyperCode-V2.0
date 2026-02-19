export interface Task {
  id: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  assignedAgent?: string;
  duration?: string;
  order: number;
  completedAt?: string; // ISO Date string
}

export interface Phase {
  id: string;
  title: string;
  description?: string;
  tasks: Task[];
  status: 'pending' | 'in_progress' | 'completed';
  estimatedTime?: string;
  order: number;
}

export interface ProjectPlan {
  id: string;
  title: string;
  description?: string;
  phases: Phase[];
  userId: string;
  createdAt: string;
  updatedAt: string;
  version: number;
  isPublic: boolean;
}

export interface PlanViewerProps {
  plan: ProjectPlan;
  onTaskStatusChange?: (phaseId: string, taskId: string, newStatus: Task['status']) => void;
  onPhaseStatusChange?: (phaseId: string, newStatus: Phase['status']) => void;
  readOnly?: boolean;
  className?: string;
}
