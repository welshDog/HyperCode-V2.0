import React, { useState } from 'react';
import { ProjectPlan, Phase, Task } from './types';
import ReactMarkdown from 'react-markdown';
import { 
  CheckCircle2, 
  Circle, 
  Clock, 
  ChevronDown, 
  ChevronRight, 
  Calendar,
  AlertCircle
} from 'lucide-react';

// --- Styles ---
const styles = {
  container: {
    fontFamily: 'var(--font-ui, sans-serif)',
    color: 'var(--color-text, #e2e8f0)',
    backgroundColor: 'var(--color-bg, #0f172a)',
    borderRadius: '0.5rem',
    padding: '1.5rem',
    border: '1px solid var(--color-panel, #1e293b)',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  header: {
    marginBottom: '2rem',
    borderBottom: '1px solid var(--color-panel, #1e293b)',
    paddingBottom: '1rem',
  },
  title: {
    fontSize: '1.875rem',
    fontWeight: 'bold',
    color: 'var(--color-primary, #818cf8)',
    marginBottom: '0.5rem',
  },
  meta: {
    display: 'flex',
    gap: '1.5rem',
    fontSize: '0.875rem',
    color: '#94a3b8',
    alignItems: 'center',
  },
  phaseList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '1rem',
  },
  phaseCard: {
    backgroundColor: 'var(--color-panel, #1e293b)',
    borderRadius: '0.5rem',
    overflow: 'hidden',
    border: '1px solid #334155',
  },
  phaseHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '1rem',
    cursor: 'pointer',
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
  },
  phaseTitle: {
    fontSize: '1.125rem',
    fontWeight: '600',
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
  },
  taskList: {
    padding: '1rem',
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
  },
  taskItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '0.75rem',
    padding: '0.75rem',
    borderBottom: '1px solid #334155',
  },
  taskCheckbox: {
    marginTop: '0.25rem',
    cursor: 'pointer',
    color: 'var(--color-secondary, #22d3ee)',
  },
  statusBadge: (status: string) => ({
    padding: '0.25rem 0.5rem',
    borderRadius: '9999px',
    fontSize: '0.75rem',
    fontWeight: '500',
    backgroundColor: status === 'completed' ? 'rgba(34, 197, 94, 0.2)' : 
                     status === 'in_progress' ? 'rgba(59, 130, 246, 0.2)' : 
                     'rgba(148, 163, 184, 0.2)',
    color: status === 'completed' ? '#4ade80' : 
           status === 'in_progress' ? '#60a5fa' : 
           '#94a3b8',
  })
};

interface PlanViewerProps {
  plan: ProjectPlan;
  onTaskStatusChange?: (phaseId: string, taskId: string, newStatus: Task['status']) => void;
  onPhaseStatusChange?: (phaseId: string, newStatus: Phase['status']) => void;
  readOnly?: boolean;
}

const PhaseItem: React.FC<{
  phase: Phase;
  onTaskToggle: (taskId: string, currentStatus: Task['status']) => void;
  isExpanded: boolean;
  onToggleExpand: () => void;
  readOnly?: boolean;
}> = ({ phase, onTaskToggle, isExpanded, onToggleExpand, readOnly }) => {
  
  return (
    <div style={styles.phaseCard}>
      <div 
        style={styles.phaseHeader} 
        onClick={onToggleExpand}
        role="button"
        aria-expanded={isExpanded}
        tabIndex={0}
        onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onToggleExpand();
            }
        }}
      >
        <div style={styles.phaseTitle}>
          {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
          <span>{phase.title}</span>
          <span style={styles.statusBadge(phase.status)}>{phase.status.replace('_', ' ')}</span>
        </div>
        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.875rem', color: '#94a3b8' }}>
          {phase.estimatedTime && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Clock size={14} />
              {phase.estimatedTime}
            </div>
          )}
        </div>
      </div>
      
      {isExpanded && (
        <div style={styles.taskList}>
          {phase.description && (
            <div style={{ marginBottom: '1rem', color: '#cbd5e1', fontSize: '0.9rem' }}>
              <ReactMarkdown>{phase.description}</ReactMarkdown>
            </div>
          )}
          
          {phase.tasks.map(task => (
            <div key={task.id} style={styles.taskItem}>
               <div 
                 style={{ 
                    ...styles.taskCheckbox, 
                    opacity: readOnly ? 0.5 : 1, 
                    cursor: readOnly ? 'default' : 'pointer' 
                 }}
                 onClick={() => !readOnly && onTaskToggle(task.id, task.status)}
               >
                 {task.status === 'completed' ? (
                   <CheckCircle2 size={20} color="var(--color-secondary, #22d3ee)" />
                 ) : (
                   <Circle size={20} color="#64748b" />
                 )}
               </div>
               <div style={{ flex: 1 }}>
                 <div style={{ 
                   textDecoration: task.status === 'completed' ? 'line-through' : 'none',
                   color: task.status === 'completed' ? '#64748b' : '#e2e8f0'
                 }}>
                   {task.description}
                 </div>
                 <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
                    {task.assignedAgent && (
                        <span style={{ fontSize: '0.75rem', color: '#a78bfa', backgroundColor: 'rgba(139, 92, 246, 0.1)', padding: '0 0.25rem', borderRadius: '4px' }}>
                            @{task.assignedAgent}
                        </span>
                    )}
                    {task.duration && (
                        <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                            {task.duration}
                        </span>
                    )}
                 </div>
               </div>
            </div>
          ))}
          
          {phase.tasks.length === 0 && (
             <div style={{ padding: '1rem', textAlign: 'center', color: '#64748b', fontStyle: 'italic' }}>
                No tasks defined for this phase.
             </div>
          )}
        </div>
      )}
    </div>
  );
};

export const PlanViewer: React.FC<PlanViewerProps> = ({ 
  plan, 
  onTaskStatusChange,
  readOnly = false 
}) => {
  const [expandedPhases, setExpandedPhases] = useState<Set<string>>(new Set([plan.phases[0]?.id]));

  const togglePhase = (phaseId: string) => {
    const newExpanded = new Set(expandedPhases);
    if (newExpanded.has(phaseId)) {
      newExpanded.delete(phaseId);
    } else {
      newExpanded.add(phaseId);
    }
    setExpandedPhases(newExpanded);
  };

  const handleTaskToggle = (phaseId: string, taskId: string, currentStatus: Task['status']) => {
      if (onTaskStatusChange) {
          const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
          onTaskStatusChange(phaseId, taskId, newStatus);
      }
  };

  if (!plan) {
      return (
          <div style={{...styles.container, textAlign: 'center', color: '#ef4444'}}>
              <AlertCircle size={48} style={{margin: '0 auto 1rem auto'}} />
              <h2>No Plan Data Available</h2>
          </div>
      )
  }

  // Calculate stats
  const totalTasks = plan.phases.reduce((acc, phase) => acc + phase.tasks.length, 0);
  const completedTasks = plan.phases.reduce((acc, phase) => acc + phase.tasks.filter(t => t.status === 'completed').length, 0);
  const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div style={styles.container} className="plan-viewer">
      <header style={styles.header}>
        <h1 style={styles.title}>{plan.title}</h1>
        <div style={styles.meta}>
           <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Calendar size={16} />
              Created: {new Date(plan.createdAt).toLocaleDateString()}
           </div>
           <div>
              Version {plan.version}
           </div>
           <div style={{ marginLeft: 'auto', fontWeight: 'bold', color: 'var(--color-secondary, #22d3ee)' }}>
              {progress}% Complete
           </div>
        </div>
        {/* Progress Bar */}
        <div style={{ 
            height: '4px', 
            backgroundColor: '#334155', 
            marginTop: '1rem', 
            borderRadius: '2px', 
            overflow: 'hidden' 
        }}>
            <div style={{ 
                width: `${progress}%`, 
                height: '100%', 
                backgroundColor: 'var(--color-secondary, #22d3ee)',
                transition: 'width 0.3s ease'
            }} />
        </div>
      </header>

      <div style={styles.phaseList}>
        {plan.phases.map(phase => (
          <PhaseItem 
            key={phase.id} 
            phase={phase} 
            isExpanded={expandedPhases.has(phase.id)}
            onToggleExpand={() => togglePhase(phase.id)}
            onTaskToggle={(taskId, status) => handleTaskToggle(phase.id, taskId, status)}
            readOnly={readOnly}
          />
        ))}
      </div>
    </div>
  );
};

export default PlanViewer;
