"use client"
import React, { useState } from 'react';
import PlanViewer from '../../src/components/plan/PlanViewer';
import { PlanEditor } from '../../src/components/plan/PlanEditor';
import { ProjectPlan, Phase, Task } from '../../src/components/plan/types';

const initialPlan: ProjectPlan = {
  id: 'demo-plan-1',
  title: 'Interactive Plan Mode Demo',
  description: 'A demonstration plan for testing the PlanViewer component.',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  version: 1,
  userId: 'user-demo',
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
};

export default function PlanDemoPage() {
  const [plan, setPlan] = useState<ProjectPlan>(initialPlan);
  const [isEditing, setIsEditing] = useState(false);

  const handleTaskStatusChange = (phaseId: string, taskId: string, newStatus: Task['status']) => {
    setPlan(prevPlan => {
      const newPhases = prevPlan.phases.map(phase => {
        if (phase.id === phaseId) {
          const newTasks = phase.tasks.map(task => {
            if (task.id === taskId) {
              return { ...task, status: newStatus };
            }
            return task;
          });
          
          // Auto-update phase status logic (simplified)
          const allCompleted = newTasks.every(t => t.status === 'completed');
          const anyInProgress = newTasks.some(t => t.status === 'in_progress' || t.status === 'completed');
          let newPhaseStatus = phase.status;
          
          if (allCompleted) newPhaseStatus = 'completed';
          else if (anyInProgress) newPhaseStatus = 'in_progress';
          else newPhaseStatus = 'pending';

          return { ...phase, tasks: newTasks, status: newPhaseStatus };
        }
        return phase;
      });
      return { ...prevPlan, phases: newPhases };
    });
  };

  return (
    <div style={{ minHeight: '100vh', padding: '2rem', backgroundColor: '#0f172a' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div className="flex justify-between items-center mb-8">
            <h1 style={{ color: '#fff', fontSize: '2rem' }}>Plan Viewer Component Demo</h1>
            <button 
              onClick={() => setIsEditing(!isEditing)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors font-medium"
              style={{ backgroundColor: '#2563eb', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.375rem', cursor: 'pointer' }}
            >
              {isEditing ? 'Cancel Editing' : 'Edit Plan'}
            </button>
        </div>

        <div style={{ marginBottom: '2rem', color: '#94a3b8' }}>
          <p>This page demonstrates the PlanViewer and PlanEditor components. Toggle edit mode to modify the plan structure.</p>
        </div>
        
        {isEditing ? (
            <PlanEditor initialPlan={plan} mode="edit" />
        ) : (
            <PlanViewer 
              plan={plan} 
              onTaskStatusChange={handleTaskStatusChange}
            />
        )}

        <div style={{ marginTop: '4rem', borderTop: '1px solid #334155', paddingTop: '2rem' }}>
          <h2 style={{ color: '#fff', marginBottom: '1rem' }}>Read-Only Mode</h2>
          <PlanViewer 
            plan={plan} 
            readOnly={true}
          />
        </div>
      </div>
    </div>
  );
}
