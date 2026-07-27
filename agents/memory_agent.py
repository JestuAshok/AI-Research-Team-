import time
import json
from graphs.state import AgentState
from database.db import update_session_results, update_session_status
from memory.vector_db import index_research

def memory_node(state: AgentState) -> dict:
    """
    Memory Agent Node.
    Saves final reports, summary schemas, and source nodes into database logs.
    Indexes semantic contents inside vector store for future recall.
    """
    start_time = time.time()
    session_id = state.get("session_id", "")
    topic = state.get("topic", "")
    summary_data = state.get("summary", {})
    verified_list = state.get("verified_results", [])
    report_paths = state.get("report_paths", {})
    confidence_score = state.get("confidence_score", 85.0)
    
    print(f"[{session_id}] [AGENT] Memory Agent: Storing session state and indexing contents.")
    update_session_status(session_id, "storing")
    
    # Consolidate verified source data
    web_sources = []
    papers = []
    for item in verified_list:
        web_sources.extend(item.get("web_sources", []))
        papers.extend(item.get("papers", []))
        
    sources_data = {
        "web_sources": web_sources,
        "papers": papers
    }
    
    # Compile text representation for semantic memory indexing
    exec_summary = summary_data.get("executive_summary", "")
    findings_list = []
    for f in summary_data.get("findings", []):
        findings_list.append(f"{f.get('subtopic')}: {f.get('details')}")
    findings_text = "\n".join(findings_list)
    
    indexing_content = (
        f"Research Topic: {topic}\n\n"
        f"Executive Summary: {exec_summary}\n\n"
        f"Detailed Findings:\n{findings_text}\n\n"
        f"Confidence Score: {confidence_score}%"
    )
    
    # Index in vector storage
    try:
        index_research(
            session_id=session_id,
            topic=topic,
            content=indexing_content,
            metadata={
                "confidence_score": confidence_score,
                "pdf_report": report_paths.get("pdf", ""),
                "docx_report": report_paths.get("docx", "")
            }
        )
    except Exception as e:
        print(f"[!] Memory Agent: Semantic indexing failed: {e}")
        
    duration = time.time() - start_time
    
    log_entry = {
        "agent": "Memory Agent",
        "status": "completed",
        "duration": round(duration, 2),
        "output": f"Indexed research state in memory. Saved session database entry.",
        "details": {
            "session_id": session_id,
            "indexed_length": len(indexing_content)
        },
        "timestamp": time.time()
    }
    
    # Collate all logs (the current step logs + past step logs)
    all_logs = state.get("agent_logs", []) + [log_entry]
    
    # Write final results to SQLite
    try:
        update_session_results(
            session_id=session_id,
            status="completed",
            confidence_score=confidence_score,
            summary_data=summary_data,
            sources_data=sources_data,
            agent_logs=all_logs,
            pdf_path=report_paths.get("pdf", ""),
            docx_path=report_paths.get("docx", "")
        )
        print(f"[SUCCESS] Session {session_id} results updated in SQLite database.")
    except Exception as e:
        print(f"[ERROR] Memory Agent: Database write failed: {e}")
        
    return {
        "agent_logs": [log_entry],
        "status": "completed"
    }
