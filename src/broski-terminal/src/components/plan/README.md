# PlanViewer Component

The `PlanViewer` component is a React component designed to display project plans, phases, and tasks in an interactive and responsive layout. It supports markdown rendering for descriptions, collapsible phases, and task status toggling.

## Features

- **Responsive Design**: Adapts to different screen sizes.
- **Interactive**: Expand/collapse phases, toggle task status.
- **Markdown Support**: Renders rich text descriptions for phases using `react-markdown`.
- **Accessibility**: ARIA attributes for expand/collapse actions.
- **Customizable**: Accepts custom styles and callbacks.

## Usage

```tsx
import { PlanViewer } from '@/components/plan/PlanViewer';
import { ProjectPlan } from '@/components/plan/types';

const myPlan: ProjectPlan = {
  id: 'plan-1',
  title: 'My Project Plan',
  phases: [
    {
      id: 'phase-1',
      title: 'Planning',
      status: 'in_progress',
      tasks: [
        { id: 't1', description: 'Define scope', status: 'completed' },
        { id: 't2', description: 'Create timeline', status: 'pending' }
      ]
    }
  ],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  version: 1
};

export default function MyPage() {
  return (
    <PlanViewer 
      plan={myPlan} 
      onTaskStatusChange={(phaseId, taskId, newStatus) => {
        console.log(`Task ${taskId} in phase ${phaseId} changed to ${newStatus}`);
      }}
    />
  );
}
```

## Props

| Prop | Type | Description |
|------|------|-------------|
| `plan` | `ProjectPlan` | The plan data object to display. |
| `onTaskStatusChange` | `(phaseId, taskId, status) => void` | Callback when a task status is toggled. |
| `onPhaseStatusChange` | `(phaseId, status) => void` | Callback when a phase status changes. |
| `readOnly` | `boolean` | If true, disables interaction. Default `false`. |

## types.ts

The component relies on the following TypeScript interfaces defined in `types.ts`:

- `ProjectPlan`
- `Phase`
- `Task`

## Dependencies

- `react`
- `lucide-react` (for icons)
- `react-markdown` (for rendering descriptions)
