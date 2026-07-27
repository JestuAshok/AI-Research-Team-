import unittest
from fastapi.testclient import TestClient
from backend.main import app

class TestAPIEndpoints(unittest.TestCase):
    """
    Test suite for FastAPI REST API endpoints.
    """

    def setUp(self):
        self.client = TestClient(app)

    def test_get_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))

    def test_get_config_status(self):
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("demo_mode", data)
        self.assertIn("groq_configured", data)
        self.assertIn("tavily_configured", data)

    def test_get_stats(self):
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_briefs", data)
        self.assertIn("avg_confidence", data)
        self.assertIn("total_sources", data)

    def test_get_history(self):
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_start_research_endpoint(self):
        response = self.client.post("/research", json={"topic": "Autonomous AI Agents in Robotics"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("session_id", data)
        self.assertEqual(data.get("topic"), "Autonomous AI Agents in Robotics")
        self.assertEqual(data.get("status"), "planning")

        # Test querying status for the created session
        session_id = data["session_id"]
        status_res = self.client.get(f"/status/{session_id}")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertEqual(status_data.get("id"), session_id)

if __name__ == "__main__":
    unittest.main()
