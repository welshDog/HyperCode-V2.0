# Frontend Architecture

This document describes the high-level architecture of the HyperFlow Editor, focusing on the state management, component hierarchy, and integration with the backend.

## 🏗 High-Level Structure

The application is structured as a **Single Page Application (SPA)** using **React 18** and **Vite**.

-   **Routing**: Client-side routing via `react-router-dom`.
-   **Styling**: Utility-first CSS using **Tailwind CSS**.
-   **State Management**: Global state managed by **Zustand**.
-   **Data Fetching**: Custom API client (`hypercodeCoreClient`) + React Hooks.

## 📦 Core Modules

### 1. State Management (`src/stores/aiStore.ts`)
The `aiStore` acts as the single source of truth for the application's AI-related data. It manages:
-   **Agent Workflow**: Nodes and edges for the ReactFlow graph.
-   **Budget Metrics**: Total and spent budget for visualization.
-   **Task Queue**: List of pending, running, and completed tasks.
-   **Connection Status**: WebSocket connection state (`isConnected`).

#### Persistence
The store uses `persist` middleware to save state to `localStorage`, ensuring data persists across page reloads.

### 2. Networking (`src/services/hypercodeCoreClient.ts`)
A centralized service for handling API communication with the `hypercode-core` backend.
-   **REST API**: Handles CRUD operations for agents, tasks, and artifacts.
-   **WebSocket**: Manages real-time updates for agent status and budget changes.
-   **Authentication**: Uses token-based authentication (Bearer token).

### 3. Real-time Integration (`src/hooks/useAgentUpdates.ts`)
A custom hook that encapsulates WebSocket logic:
-   **Connection**: Establishes and maintains the WebSocket connection.
-   **Event Handling**: Listens for specific events (`agent:update`, `agent:complete`) and dispatches actions to the store.
-   **Reconnection**: Automatically attempts to reconnect on disconnect.

## 🧩 Component Hierarchy

The UI is composed of modular, reusable components organized by feature:

-   **`App.tsx`**: Root component, handles routing and layout.
-   **`HyperLayout.tsx`**: Main layout wrapper (sidebar, header).
-   **`pages/AIDashboard.tsx`**: Container for the AI dashboard.
    -   **`AgentWorkflow.tsx`**: Visualizes agent nodes and edges.
    -   **`BudgetGauge.tsx`**: Displays budget utilization.
    -   **`TaskQueue.tsx`**: Manages task list and creation.
-   **`pages/Editor.tsx`**: Main code editor interface.
    -   **`CodeRain.tsx`**: Visual effect component.
    -   **`MonacoEditor`**: Code editing component.

## 🔄 Data Flow

1.  **Initialization**: Upon mounting, `AIDashboard` triggers `fetchAgents` and `fetchBudget` actions via `useEffect`.
2.  **User Action**: User creates a task -> `generateAgent` action -> API call -> Store update (optimistic) -> WebSocket update (confirmation).
3.  **Real-time Update**: Backend emits `agent:update` -> WebSocket listener -> `updateAgentStatus` action -> Store update -> React re-render.

## 🔐 Security

-   **API Key**: Stored in `.env` and accessed via `import.meta.env.VITE_API_KEY`.
-   **HTTPS**: Recommended for production deployment.
-   **CORS**: Configured on the backend to allow requests from the frontend origin.
