import unittest
import json
import os
import sys

# Ensure the parent directory is in the path to import the agent module
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from agent import ProjectStrategistAgent, LOG_FILE

class TestProjectStrategistAgent(unittest.TestCase):

    def setUp(self):
        """
        Setup common test fixtures.
        """
        os.environ["TEST_MODE"] = "true"
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "business-agent.json"
        )
        self.agent = ProjectStrategistAgent(config_path=self.config_path)

    def tearDown(self):
        if "TEST_MODE" in os.environ:
            del os.environ["TEST_MODE"]

    def test_initialization(self):
        """
        Test if agent initializes with correct config.
        """
        self.assertEqual(self.agent.state, "READY")
        self.assertEqual(self.agent.config.get("name"), "Project Strategist")
        self.assertTrue("roadmap_planning" in self.agent.capabilities)

    def test_execution(self):
        """
        Test the execute method with a valid task.
        """
        task = {
            "id": "test-task-001",
            "type": "analyze_requirements",
            "description": "Evaluate Phase 2 roadmap"
        }
        
        # Mock Redis client for testing to avoid actual connection requirement in unit tests
        # We only mock if not available, but for unit tests it's safer to mock
        self.agent.redis_client = None 
        
        result = self.agent.execute(task)
        self.assertEqual(result.get("status"), "success")
        self.assertEqual(result.get("task_id"), "test-task-001")
        # Check for simulated LLM response format
        self.assertTrue("Simulated LLM response" in result.get("output"))

    def test_execution_failure(self):
        """
        Test the execute method with invalid data (simulated).
        """
        # Simulate a crash or exception handling
        # For now, our simple prototype echoes back success, but we can verify it doesn't crash
        task = {"id": "fail-task", "description": "Crash me if you can"}
        try:
            self.agent.execute(task)
        except Exception:
            self.fail("Agent execute() raised an exception unexpectedly!")

    def test_termination(self):
        """
        Test the terminate method.
        """
        self.agent.terminate()
        self.assertEqual(self.agent.state, "TERMINATED")

if __name__ == '__main__':
    unittest.main()
