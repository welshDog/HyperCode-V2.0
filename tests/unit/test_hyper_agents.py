"""Unit tests for the hyper_agents package.

Tests cover:
- HyperAgent base class (AgentStatus, AgentArchetype, NDErrorResponse)
- TestArchitect (goal creation, step management, status updates)
- TestWorker (metric recording, alert thresholds)
- WorkerAgent (task execution, status lifecycle)
- __init__.py public API surface
"""
import asyncio
import pytest

from src.agents.hyper_agents import (
    Goal,
    GoalStatus,
    HyperAgent,
    NDErrorResponse,
    PlanStep,
    WorkerAgent,
)

# --- Concrete test doubles (abstract execute() implemented) ---

class TestArchitect(TestArchitect):
    async def execute(self, task):
        return {"status": "done", "message": "test"}

class TestWorker(_TestWorker):
    async def execute(self, task):
        return {"status": "done", "message": "test"}

class TestWorker(WorkerAgent):
    async def execute(self, task):
        return {"status": "done", "message": "test"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(coro):
    """Synchronously run a coroutine for pytest compatibility."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Public API surface tests
# ---------------------------------------------------------------------------

class TestPublicAPI:
    """Verify __init__.py exports all expected symbols."""

    def test_all_symbols_importable(self):
        symbols = [
            HyperAgent, AgentStatus, AgentArchetype, NDErrorResponse,
            TestArchitect, Goal, PlanStep, GoalStatus,
            TestWorker, WorkerAgent,
        ]
        for sym in symbols:
            assert sym is not None, f"{sym} should be importable"

    def test_agent_archetype_values(self):
        assert AgentArchetype.ARCHITECT.value == "architect"
        assert AgentArchetype.WORKER.value == "worker"
        assert AgentArchetype.OBSERVER.value == "observer"

    def test_agent_status_values(self):
        for status in [
            AgentStatus.IDLE,
            AgentStatus.INITIALIZING,
            AgentStatus.BUSY,
            AgentStatus.TERMINATED,
        ]:
            assert status.value is not None


# ---------------------------------------------------------------------------
# TestArchitect tests
# ---------------------------------------------------------------------------

class TestTestArchitect:

    def setup_method(self):
        self.agent = TestArchitect(agent_id="test-architect-01")
        run(self.agent.initialize())

    def test_initialize_sets_idle_status(self):
        assert self.agent._status == AgentStatus.IDLE

    def test_create_goal_returns_id(self):
        goal_id = run(self.agent.create_goal(
            title="Test Goal",
            description="A goal for testing"
        ))
        assert isinstance(goal_id, str)
        assert len(goal_id) > 0

    def test_created_goal_is_retrievable(self):
        goal_id = run(self.agent.create_goal(title="Fetch Me", description="desc"))
        goal = self.agent.get_goal(goal_id)
        assert isinstance(goal, Goal)
        assert goal.title == "Fetch Me"
        assert goal.status == GoalStatus.DEFINED

    def test_add_step_to_goal(self):
        goal_id = run(self.agent.create_goal(title="Stepped Goal", description="d"))
        self.agent.add_step(goal_id, "step_a", "Do A")
        goal = self.agent.get_goal(goal_id)
        assert len(goal.steps) == 1
        assert goal.steps[0].step_id == "step_a"

    def test_add_step_with_dependency(self):
        goal_id = run(self.agent.create_goal(title="Dep Goal", description="d"))
        self.agent.add_step(goal_id, "step_a", "Do A")
        self.agent.add_step(goal_id, "step_b", "Do B", deps={"step_a"})
        goal = self.agent.get_goal(goal_id)
        step_b = next(s for s in goal.steps if s.step_id == "step_b")
        assert "step_a" in step_b.dependencies

    def test_get_ready_steps_respects_dependencies(self):
        goal_id = run(self.agent.create_goal(title="Ready Check", description="d"))
        self.agent.add_step(goal_id, "step_a", "Do A")
        self.agent.add_step(goal_id, "step_b", "Do B", deps={"step_a"})
        ready = self.agent.get_ready_steps(goal_id)
        assert len(ready) == 1
        assert ready[0].step_id == "step_a"

    def test_update_step_status_to_completed(self):
        goal_id = run(self.agent.create_goal(title="Update Test", description="d"))
        self.agent.add_step(goal_id, "step_x", "Do X")
        self.agent.update_step_status(goal_id, "step_x", GoalStatus.COMPLETED)
        goal = self.agent.get_goal(goal_id)
        assert goal.status == GoalStatus.COMPLETED
        assert self.agent._total_goals_completed == 1

    def test_goal_fails_if_step_fails(self):
        goal_id = run(self.agent.create_goal(title="Fail Test", description="d"))
        self.agent.add_step(goal_id, "step_f", "Fail step")
        self.agent.update_step_status(goal_id, "step_f", GoalStatus.FAILED)
        goal = self.agent.get_goal(goal_id)
        assert goal.status == GoalStatus.FAILED

    def test_register_agent(self):
        self.agent.register_agent("worker-99", AgentArchetype.WORKER)
        assert "worker-99" in self.agent._agent_registry

    def test_stats_property(self):
        stats = self.agent.stats
        assert stats["agent_id"] == "test-architect-01"
        assert "total_goals" in stats
        assert "completed_goals" in stats

    def test_goal_progress_calculation(self):
        goal_id = run(self.agent.create_goal(title="Progress", description="d"))
        self.agent.add_step(goal_id, "s1", "Step 1")
        self.agent.add_step(goal_id, "s2", "Step 2")
        self.agent.update_step_status(goal_id, "s1", GoalStatus.COMPLETED)
        goal = self.agent.get_goal(goal_id)
        assert goal.progress == pytest.approx(0.5)

    def test_shutdown(self):
        run(self.agent.shutdown())
        assert self.agent._status == AgentStatus.TERMINATED


# ---------------------------------------------------------------------------
# TestWorker tests
# ---------------------------------------------------------------------------

class Test_TestWorker:

    def setup_method(self):
        self.agent = TestWorker(agent_id="test-observer-01")
        run(self.agent.initialize())

    def test_initialize_sets_idle(self):
        assert self.agent._status == AgentStatus.IDLE

    def test_archetype_is_observer(self):
        assert self.agent.ARCHETYPE == AgentArchetype.OBSERVER

    def test_shutdown(self):
        run(self.agent.shutdown())
        assert self.agent._status == AgentStatus.TERMINATED


# ---------------------------------------------------------------------------
# WorkerAgent tests
# ---------------------------------------------------------------------------

class TestWorkerAgent:

    def setup_method(self):
        self.agent = WorkerAgent(agent_id="test-worker-01")
        run(self.agent.initialize())

    def test_initialize_sets_idle(self):
        assert self.agent._status == AgentStatus.IDLE

    def test_archetype_is_worker(self):
        assert self.agent.ARCHETYPE == AgentArchetype.WORKER

    def test_execute_task_returns_dict(self):
        result = run(self.agent.execute({"action": "ping", "payload": {}}))
        assert isinstance(result, dict)

    def test_shutdown(self):
        run(self.agent.shutdown())
        assert self.agent._status == AgentStatus.TERMINATED


# ---------------------------------------------------------------------------
# NDErrorResponse tests
# ---------------------------------------------------------------------------

class TestNDErrorResponse:

    def test_nd_error_response_has_required_fields(self):
        err = NDErrorResponse(
            error_code="TEST_001",
            message="Something went wrong",
            context={"step": "init"},
        )
        assert err.error_code == "TEST_001"
        assert "wrong" in err.message
        assert err.context["step"] == "init"
