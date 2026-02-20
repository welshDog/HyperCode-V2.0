# HyperFlow Editor

HyperFlow Editor is the frontend interface for the HyperCode ecosystem, built with React, Vite, and Tailwind CSS. It features a modern, cyber-aesthetic UI and integrates with the `hypercode-core` backend to provide real-time agent visualization, code editing, and system monitoring.

## 🚀 Features

- **Code Editor**: Monaco-based editor with syntax highlighting and intelligent features.
- **Visual Cortex (AI Dashboard)**: Real-time visualization of AI agent workflows, task queues, and budget metrics.
  - **Agent Workflow**: Interactive node-based graph (ReactFlow) showing agent status and relationships.
  - **Task Queue**: Live monitoring of task progress with priority indicators and artifact downloads.
  - **Budget Gauge**: Visual tracking of computational resource usage.
- **Real-time Updates**: WebSocket integration for sub-250ms latency updates from the backend.
- **Cyber-Aesthetic UI**: Custom Tailwind configuration for a consistent, immersive dark-mode experience.

## 🛠 Tech Stack

- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS (v4) + Lucide React (Icons)
- **State Management**: Zustand (with persistence)
- **Visualization**: ReactFlow (Workflows), Recharts (Charts)
- **Networking**: native `fetch` + `react-use-websocket`
- **Testing**: Vitest (Unit), Cypress (E2E)

## 📦 Installation

1.  **Prerequisites**: Node.js v18+ and npm.
2.  **Install Dependencies**:
    ```bash
    npm install
    ```

## 🏃‍♂️ Running the Application

### Development Mode
Start the development server with hot-reload:
```bash
npm run dev
```
Access the app at `http://localhost:5173`.

### Production Build
Build the application for production:
```bash
npm run build
```
Preview the build locally:
```bash
npm run preview
```

## 🧪 Testing

### Unit Tests
Run unit tests with Vitest:
```bash
npm test
```

### End-to-End (E2E) Tests
Run E2E tests with Cypress (requires running backend):
```bash
# Headless mode
npm run cy:run

# Interactive mode
npm run cy:open
```
See [Testing Documentation](docs/TESTING.md) for more details.

## 📚 Documentation

- [Visual Cortex (AI Dashboard)](docs/VISUAL_CORTEX.md): Detailed guide on the AI visualization components.
- [Architecture](docs/ARCHITECTURE.md): Frontend architecture and state management.
- [Testing Guide](docs/TESTING.md): Comprehensive testing instructions.
- [API Reference](docs/API_REFERENCE.md): Backend API contract.

## 🤝 Integration

The editor expects the `hypercode-core` backend to be running at `http://localhost:8000` (configurable via `.env`). It uses:
- REST API for initial data fetching and actions (e.g., generating agents).
- WebSocket (`/ws/visual-cortex`) for real-time status updates.
