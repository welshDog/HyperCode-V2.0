import useSWR, { mutate } from 'swr';
import { planService } from '../services/PlanService';
import { ProjectPlan, Task } from '../components/plan/types';

// Fetcher function for SWR removed in favor of direct service calls to fix type inference

export function usePlans() {
  const { data, error, isLoading } = useSWR<ProjectPlan[]>('/plans', () => planService.listPlans());
  return {
    plans: data,
    isLoading,
    isError: error
  };
}

export function usePlan(id: string | null) {
  const { data, error, isLoading, mutate: mutatePlan } = useSWR<ProjectPlan>(
    id ? `/plans/${id}` : null, 
    () => id ? planService.getPlan(id) : Promise.reject('No ID')
  );

  const updateTaskStatus = async (phaseId: string, taskId: string, status: Task['status']) => {
    if (!data || !id) return;

    // Create updated plan object optimistically
    const updatedPlan: ProjectPlan = {
      ...data,
      phases: data.phases.map(p => {
        if (p.id === phaseId) {
            const newTasks = p.tasks.map(t => {
                if (t.id === taskId) {
                    return { ...t, status, completedAt: status === 'completed' ? new Date().toISOString() : undefined };
                }
                return t;
            });
            
            // Check phase completion status
            const allCompleted = newTasks.every(t => t.status === 'completed');
            const anyInProgress = newTasks.some(t => t.status === 'in_progress' || t.status === 'completed');
            let newPhaseStatus = p.status;
            if (allCompleted) newPhaseStatus = 'completed';
            else if (anyInProgress) newPhaseStatus = 'in_progress';
            else newPhaseStatus = 'pending';

            return { ...p, tasks: newTasks, status: newPhaseStatus };
        }
        return p;
      })
    };

    // Optimistically update the cache
    await mutatePlan(updatedPlan, false);
    
    try {
        await planService.updateTaskStatus(id, phaseId, taskId, status);
        // Revalidate to ensure server sync
        await mutatePlan();
    } catch (err) {
        console.error('Failed to update task status:', err);
        // Rollback to original data
        await mutatePlan(data, false);
        throw err;
    }
  };

  return {
    plan: data,
    isLoading,
    isError: error,
    updateTaskStatus
  };
}
