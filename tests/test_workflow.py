import unittest
import uuid
from graphs.state import AgentState
from graphs.workflow import research_graph
from database import db

class TestWorkflow(unittest.TestCase):
    """
    Test suite for the multi-agent LangGraph workflow execution.
    """

    @classmethod
    def setUpClass(cls):
        db.init_db()

    def test_end_to_end_graph_execution(self):
        session_id = str(uuid.uuid4())
        topic = "Quantum Computing in Drug Discovery"
        
        db.create_session(session_id, topic)
        
        initial_state: AgentState = {
            "session_id": session_id,
            "topic": topic,
            "plan": [],
            "raw_results": [],
            "verified_results": [],
            "summary": {},
            "confidence_score": 0.0,
            "report_paths": {},
            "agent_logs": [],
            "status": "planning"
        }

        final_state = research_graph.invoke(initial_state)

        # Assertions
        self.assertEqual(final_state.get("status"), "completed")
        self.assertGreater(len(final_state.get("plan", [])), 0)
        self.assertGreaterEqual(final_state.get("confidence_score", 0), 0)
        self.assertIn("pdf", final_state.get("report_paths", {}))
        self.assertIn("docx", final_state.get("report_paths", {}))
        self.assertGreater(len(final_state.get("agent_logs", [])), 0)

        # Verify database record update
        session_record = db.get_session(session_id)
        self.assertIsNotNone(session_record)
        self.assertEqual(session_record.get("status"), "completed")

if __name__ == "__main__":
    unittest.main()
