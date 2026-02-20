import unittest
import asyncio
import os
import sys
import shutil
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.agents.nexus.bridge.server import app
from src.agents.nexus.weaver.agent import WeaverAgent

class TestBridgeWebSocket(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_websocket_connection(self):
        with self.client.websocket_connect("/ws/bridge") as websocket:
            # Send ping
            websocket.send_json({"type": "ping"})
            # Expect pong
            response = websocket.receive_json()
            self.assertEqual(response, {"type": "pong"})

    def test_broadcast(self):
        # Trigger broadcast via API
        response = self.client.post("/api/inject-message", json={"type": "test", "payload": "hello"})
        self.assertEqual(response.status_code, 200)
        
        # Verify it works (integration test would need real client listening)
        # Here we just check the endpoint didn't crash

class TestWeaverVectorDB(unittest.TestCase):
    def setUp(self):
        self.test_path = "./data/chroma_unittest"
        self.weaver = WeaverAgent(persist_path=self.test_path)

    def tearDown(self):
        # Cleanup ChromaDB
        if os.path.exists(self.test_path):
            try:
                shutil.rmtree(self.test_path)
            except Exception as e:
                print(f"Cleanup error: {e}")

    def test_ingest_and_retrieve(self):
        # Run async method in sync test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Ingest
        loop.run_until_complete(
            self.weaver.ingest_context("test", "This is a unit test for ChromaDB.")
        )
        
        # Retrieve
        results = loop.run_until_complete(
            self.weaver.retrieve_context("unit test")
        )
        
        self.assertTrue(len(results) > 0)
        self.assertIn("unit test", results[0]["content"])
        loop.close()

if __name__ == "__main__":
    unittest.main()
