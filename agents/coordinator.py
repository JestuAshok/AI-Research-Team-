import time
import json
from graphs.state import AgentState
from backend.llm import call_llm
from database.db import update_session_status

def coordinator_node(state: AgentState) -> dict:
    """
    Coordinator Agent Node.
    Analyzes the user's research topic and generates a plan of 4-5 subtopics/search queries.
    """
    start_time = time.time()
    topic = state.get("topic", "")
    session_id = state.get("session_id", "")
    
    print(f"[{session_id}] [AGENT] Coordinator: Planning research for topic: '{topic}'")
    update_session_status(session_id, "planning")
    
    system_prompt = (
        "You are the Lead Coordinator for an AI Research Team. "
        "Your goal is to take a research topic and split it into 4 to 5 key subtopics or search queries. "
        "Provide your response in JSON format. The JSON must contain a single key 'subtopics' which maps to a list of strings."
    )
    
    user_prompt = (
        f"Research topic: {topic}\n\n"
        "Generate 4-5 key research areas or subtopics to guide our research agents. Make them specific and informative."
    )
    
    # Call Groq LLM
    response_text = call_llm(system_prompt, user_prompt, json_mode=True)
    
    try:
        data = json.loads(response_text)
        plan = data.get("subtopics", [])
    except Exception as e:
        print(f"[!] Coordinator: Error parsing LLM response: {e}. Using fallback plan.")
        plan = [
            "Core Technologies and Foundations",
            "State of Industry Deployment",
            "Primary Challenges and Bottlenecks",
            "Future Scope and Advancements"
        ]
        
    duration = time.time() - start_time
    
    log_entry = {
        "agent": "Coordinator",
        "status": "completed",
        "duration": round(duration, 2),
        "output": f"Constructed a {len(plan)}-point structured research plan.",
        "details": plan,
        "timestamp": time.time()
    }
    
    return {
        "plan": plan,
        "agent_logs": [log_entry],
        "status": "searching"
    }
