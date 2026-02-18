# HyperCode Agent Orchestrator

The central nervous system of the HyperCode Multi-Agent System.

## 🚀 Features

- **Dynamic Swarm Management**: Activates specific agent crews based on the project phase.
- **Quality Gates**: Enforces validation checks before phase transitions.
- **Handoff Protocol**: Structured task delegation between agents.
- **Redis Integration**: Distributed state and message bus.

## 🛠️ API Endpoints

### Phase Management
- `POST /phase/{phase_name}`: Switch project phase (e.g., "development", "testing").
- `GET /crew`: Get the current active agent crew.
- `GET /validate-transition?target_phase={phase}`: Check quality gates.

### Task Execution
- `POST /plan`: Submit a high-level task for planning.
- `POST /handoff`: Transfer a task between agents.
- `POST /workflow/{type}`: Start a predefined workflow (feature, bugfix).

## 🧩 Architecture

The Orchestrator uses `swarm_manager.py` to determine which agents should be active and `quality_gates.py` to ensure standards are met.

### Phases
1. **Planning**: Project Strategist, Idea Alchemist
2. **Architecture**: System Architect, Database Architect
3. **Development**: Frontend/Backend Specialists
4. **Testing**: QA Engineer, Security Engineer
5. **Deployment**: DevOps Engineer

## 📦 Usage

```bash
# Switch to Development Phase
curl -X POST http://localhost:8000/phase/development

# Check Active Crew
curl http://localhost:8000/crew

# Submit a Task
curl -X POST http://localhost:8000/plan -d '{"task": "Build login page"}'
```
