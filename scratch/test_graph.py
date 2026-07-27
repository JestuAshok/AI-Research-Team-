import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uuid
from graphs.workflow import research_graph
from database import db

# Initialize db
db.init_db()

session_id = str(uuid.uuid4())
topic = "Generative AI in Medicine"

print(f"Starting test research session for: {topic}")
db.create_session(session_id, topic)

initial_state = {
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

try:
    final_state = research_graph.invoke(initial_state)
    print("\n--- TEST RUN SUCCESSFUL ---")
    print(f"Status: {final_state.get('status')}")
    print(f"Confidence Score: {final_state.get('confidence_score')}%")
    print(f"Generated Reports: {final_state.get('report_paths')}")
    print(f"Agent Log Count: {len(final_state.get('agent_logs'))}")
except Exception as e:
    print(f"\n--- TEST RUN FAILED ---")
    import traceback
    traceback.print_exc()
