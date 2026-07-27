import time
from graphs.state import AgentState
from tools.tavily_tool import search_tavily
from tools.arxiv_tool import search_arxiv
from database.db import update_session_status

def research_node(state: AgentState) -> dict:
    """
    Research Agent Node.
    Iterates over the generated subtopics, calling Tavily and arXiv to gather literature and source documents.
    """
    start_time = time.time()
    plan = state.get("plan", [])
    session_id = state.get("session_id", "")
    
    print(f"[{session_id}] [AGENT] Researcher: Commencing search for {len(plan)} subtopics.")
    update_session_status(session_id, "searching")
    
    collected_web = []
    collected_papers = []
    
    # Iterate through the subtopics and perform research
    for subtopic in plan:
        print(f"[RESEARCH] Researching: '{subtopic}'")
        
        # Web Search
        web_results = search_tavily(subtopic, max_results=2)
        collected_web.extend(web_results)
        
        # arXiv Papers
        arxiv_results = search_arxiv(subtopic, max_results=2)
        collected_papers.extend(arxiv_results)
        
        # Add a tiny delay to respect rate limits if query is real
        time.sleep(0.5)
        
    duration = time.time() - start_time
    
    raw_results = {
        "web_sources": collected_web,
        "papers": collected_papers
    }
    
    log_entry = {
        "agent": "Research Agent",
        "status": "completed",
        "duration": round(duration, 2),
        "output": f"Gathered {len(collected_web)} web sources and {len(collected_papers)} academic papers from arXiv.",
        "details": {
            "web_count": len(collected_web),
            "paper_count": len(collected_papers)
        },
        "timestamp": time.time()
    }
    
    return {
        "raw_results": [raw_results],
        "agent_logs": [log_entry],
        "status": "verifying"
    }
