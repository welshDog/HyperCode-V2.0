import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import PlanViewer from '../../../src/components/plan/PlanViewer';
import { ProjectPlan, Phase, Task } from '../../../src/components/plan/types';

// Mock Lucide icons to avoid rendering issues in test environment if not supported
vi.mock('lucide-react', () => ({
  CheckCircle2: () => <span data-testid="icon-check-circle" />,
  Circle: () => <span data-testid="icon-circle" />,
  Clock: () => <span data-testid="icon-clock" />,
  ChevronDown: () => <span data-testid="icon-chevron-down" />,
  ChevronRight: () => <span data-testid="icon-chevron-right" />,
  Calendar: () => <span data-testid="icon-calendar" />,
  AlertCircle: () => <span data-testid="icon-alert-circle" />,
}));

// Mock ReactMarkdown to simplify testing
vi.mock('react-markdown', () => ({
  default: ({ children }: { children: string }) => <div data-testid="markdown">{children}</div>
}));

const mockPlan: ProjectPlan = {
  id: 'plan-1',
  title: 'Test Project Plan',
  createdAt: '2023-01-01T00:00:00.000Z',
  updatedAt: '2023-01-02T00:00:00.000Z',
  version: 1,
  phases: [
    {
      id: 'phase-1',
      title: 'Phase 1',
      status: 'in_progress',
      estimatedTime: '2 days',
      description: 'Phase 1 description',
      tasks: [
        { id: 't1', description: 'Task 1', status: 'completed' },
        { id: 't2', description: 'Task 2', status: 'pending' }
      ]
    },
    {
      id: 'phase-2',
      title: 'Phase 2',
      status: 'pending',
      tasks: []
    }
  ]
};

describe('PlanViewer Component', () => {
  it('renders plan title and metadata', () => {
    render(<PlanViewer plan={mockPlan} />);
    
    expect(screen.getByText('Test Project Plan')).toBeDefined();
    expect(screen.getByText(/Version 1/)).toBeDefined();
    expect(screen.getByText(/50% Complete/)).toBeDefined(); // 1 of 2 tasks completed
  });

  it('renders phases correctly', () => {
    render(<PlanViewer plan={mockPlan} />);
    
    expect(screen.getByText('Phase 1')).toBeDefined();
    expect(screen.getByText('Phase 2')).toBeDefined();
    expect(screen.getByText('in progress')).toBeDefined(); // status badge
  });

  it('expands first phase by default and shows tasks', () => {
    render(<PlanViewer plan={mockPlan} />);
    
    expect(screen.getByText('Task 1')).toBeDefined();
    expect(screen.getByText('Task 2')).toBeDefined();
    expect(screen.getByTestId('markdown')).toBeDefined();
    expect(screen.getByText('Phase 1 description')).toBeDefined();
  });

  it('collapses phase on click', () => {
    render(<PlanViewer plan={mockPlan} />);
    
    const phaseHeader = screen.getByText('Phase 1');
    fireEvent.click(phaseHeader);
    
    // After collapse, tasks should not be visible
    expect(screen.queryByText('Task 1')).toBeNull();
  });

  it('expands phase on click', () => {
    render(<PlanViewer plan={mockPlan} />);
    
    // Phase 2 is initially collapsed (only first is expanded by default in my implementation?)
    // Wait, my implementation expands first phase by default: useState(new Set([plan.phases[0]?.id]))
    
    const phaseHeader2 = screen.getByText('Phase 2');
    fireEvent.click(phaseHeader2);
    
    expect(screen.getByText('No tasks defined for this phase.')).toBeDefined();
  });

  it('calls onTaskStatusChange when task is clicked', () => {
    const handleStatusChange = vi.fn();
    render(<PlanViewer plan={mockPlan} onTaskStatusChange={handleStatusChange} />);
    
    const taskCheckbox = screen.getAllByTestId('icon-check-circle')[0].parentElement;
    if (taskCheckbox) {
        fireEvent.click(taskCheckbox);
        expect(handleStatusChange).toHaveBeenCalledWith('phase-1', 't1', 'pending');
    } else {
        throw new Error('Task checkbox not found');
    }
  });

  it('does not call onTaskStatusChange in readOnly mode', () => {
    const handleStatusChange = vi.fn();
    render(<PlanViewer plan={mockPlan} onTaskStatusChange={handleStatusChange} readOnly={true} />);
    
    const taskCheckbox = screen.getAllByTestId('icon-check-circle')[0].parentElement;
    if (taskCheckbox) {
        fireEvent.click(taskCheckbox);
        expect(handleStatusChange).not.toHaveBeenCalled();
    }
  });
});
