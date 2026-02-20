# Visual Cortex (AI Dashboard)

The **Visual Cortex** is the central nervous system of the HyperCode Editor, providing real-time visibility into the autonomous AI agents, budget utilization, and task execution pipeline.

## 🎯 Overview

The Visual Cortex is a dedicated dashboard page (`/dashboard`) that integrates three key components:
1.  **Agent Workflow**: A dynamic node graph visualizing agent interactions and statuses.
2.  **Budget Gauge**: A circular progress indicator tracking compute resource consumption.
3.  **Task Queue**: A prioritized list of pending, running, and completed tasks.

These components are powered by a unified **Zustand store** (`aiStore`) and updated via **WebSocket** connections to the `hypercode-core` backend, ensuring sub-250ms latency for status updates.

## 🧩 Components

### 1. Agent Workflow (`src/components/ai-visualization/AgentWorkflow.tsx`)
-   **Library**: `reactflow`
-   **Functionality**:
    -   Displays agents as nodes with custom styling based on status (`idle`, `working`, `completed`, `failed`).
    -   Updates node colors and icons in real-time.
    -   Includes a mini-map and interactive controls (pan/zoom).
-   **State Integration**: Consumes `nodes` and `edges` from `aiStore`.

### 2. Budget Gauge (`src/components/ai-visualization/BudgetGauge.tsx`)
-   **Library**: `recharts`
-   **Functionality**:
    -   Visualizes `spentBudget` vs `totalBudget` using a radial bar chart.
    -   Color-coded indicators:
        -   **Green**: < 50% usage
        -   **Yellow**: 50-80% usage
        -   **Red**: > 80% usage
    -   Displays numeric values and percentage in the center.

### 3. Task Queue (`src/components/ai-visualization/TaskQueue.tsx`)
-   **Library**: `lucide-react` (icons), `clsx` (styling)
-   **Functionality**:
    -   **Task Creation**: Allows users to input a prompt and generate a new agent task via the `+` button.
    -   **Progress Tracking**: Shows a progress bar for running tasks.
    -   **Artifact Download**: Provides a download link for generated artifacts (e.g., Python scripts) upon completion.
    -   **Priority Badges**: Visual indicators for `low`, `medium`, and `high` priority tasks.

## 🔄 Data Flow & State Management

The application uses **Zustand** for global state management, with persistence enabled to retain state across reloads.

### `aiStore` (`src/stores/aiStore.ts`)
-   **State Slices**:
    -   `nodes` / `edges`: Graph data for ReactFlow.
    -   `totalBudget` / `spentBudget`: Financial metrics.
    -   `tasks`: Array of task objects with status and progress.
    -   `isConnected`: WebSocket connection status.
-   **Actions**:
    -   `fetchAgents()`: Initial REST call to populate the graph.
    -   `generateAgent(prompt)`: POST request to create a new agent task.
    -   `updateAgentStatus(id, status)`: Updates a specific agent's status (triggered via WebSocket).
    -   `addTask`, `updateTaskStatus`: Manages the task queue.

### Real-time Integration (`src/hooks/useAgentUpdates.ts`)
-   **Library**: `react-use-websocket`
-   **Mechanism**:
    -   Establishes a WebSocket connection to `/ws/visual-cortex`.
    -   Listens for `agent:update`, `agent:complete`, and `agent:error` events.
    -   Dispatches actions to `aiStore` to update UI state instantly.
    -   Handles automatic reconnection with exponential backoff.

## 🚀 Usage

1.  **Navigate**: Click on the "Dashboard" icon in the sidebar or go to `/dashboard`.
2.  **Monitor**: Watch real-time updates as agents process tasks.
3.  **Create Task**: Click the `+` icon in the Task Queue, enter a prompt, and hit "Generate".
4.  **Download**: Once a task is complete, click the "Download Artifact" link to retrieve the generated code.

## 🛠 Configuration

-   **Backend URL**: Configured via `VITE_HYPERCODE_CORE_URL` in `.env` (default: `http://localhost:8000`).
-   **API Key**: Securely passed via `VITE_API_KEY`.
