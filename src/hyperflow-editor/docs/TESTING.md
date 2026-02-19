# Testing Guide

This document outlines the testing strategy for the HyperFlow Editor, covering unit tests (Vitest) and end-to-end integration tests (Cypress).

## 🧪 Unit Testing

Unit tests focus on isolated component behavior and pure function logic.

### Framework
-   **Runner**: [Vitest](https://vitest.dev/)
-   **Testing Library**: React Testing Library (`@testing-library/react`)

### Running Tests
To run the full suite:
```bash
npm test
```

### Writing Unit Tests
-   **Location**: `src/**/*.test.tsx` or `tests/`
-   **Conventions**:
    -   Use `describe` for grouping related tests.
    -   Use `it` or `test` for individual test cases.
    -   Mock dependencies using `vi.mock()`.
    -   Snapshot testing for UI components.

## 🎭 End-to-End (E2E) Testing

End-to-End tests verify the complete application flow, including backend integration and real-time updates.

### Framework
-   **Runner**: [Cypress](https://www.cypress.io/)
-   **Config**: `cypress.config.ts`

### Setup
Ensure the frontend (`npm run dev`) and backend (`hypercode-core`) are running before executing E2E tests.

### Running Tests

#### Headless Mode (CI/CD)
Run tests in the terminal without opening the Cypress GUI:
```bash
npm run cy:run
```

#### Interactive Mode (Local Development)
Open the Cypress Test Runner for debugging:
```bash
npm run cy:open
```

### Test Scenarios (`cypress/e2e/`)

#### 1. Agent Generation (`agent_generation.cy.ts`)
This test validates the full lifecycle of creating an AI agent task:
-   **User Action**: Clicks the "+" button in the Task Queue and submits a prompt ("Build a Python function...").
-   **API Integration**: Verifies the `POST /api/v1/ai/generate` request returns a `201 Created` status.
-   **Real-time Update**: Waits for the task status to transition from `pending` -> `running` -> `completed` (simulating WebSocket events).
-   **Visual Verification**: Checks that the "Visual Cortex" graph updates with new nodes and edges.
-   **Artifact Retrieval**: Confirms the "Download Artifact" link appears for completed tasks.

## 🛠 Configuration

-   **Base URL**: `http://localhost:5173` (configured in `cypress.config.ts`)
-   **Timeout**: Default command timeout set to `10000ms` (10s).
-   **Custom Commands**: Defined in `cypress/support/commands.ts`.
