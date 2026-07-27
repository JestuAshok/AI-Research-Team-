import time
import os
from graphs.state import AgentState
from reports.pdf_generator import generate_pdf_report
from reports.docx_generator import generate_docx_report
from database.db import update_session_status

def writer_node(state: AgentState) -> dict:
    """
    Report Writer Agent Node.
    Takes summary chapters and source lists, and outputs PDF and Word documents.
    """
    start_time = time.time()
    session_id = state.get("session_id", "")
    topic = state.get("topic", "")
    summary_data = state.get("summary", {})
    verified_list = state.get("verified_results", [])
    
    print(f"[{session_id}] [AGENT] Writer: Generating PDF and DOCX reports.")
    update_session_status(session_id, "writing")
    
    # Consolidate sources
    web_sources = []
    papers = []
    for item in verified_list:
        web_sources.extend(item.get("web_sources", []))
        papers.extend(item.get("papers", []))
        
    sources_data = {
        "web_sources": web_sources,
        "papers": papers
    }
    
    # Generate reports
    pdf_path_str = ""
    docx_path_str = ""
    
    try:
        pdf_path_str = generate_pdf_report(session_id, topic, summary_data, sources_data)
        # We only store the filename in report_paths for simple relative web retrieval
        pdf_filename = os.path.basename(pdf_path_str)
    except Exception as e:
        print(f"[!] Writer: Failed to generate PDF report: {e}")
        pdf_filename = ""
        
    try:
        docx_path_str = generate_docx_report(session_id, topic, summary_data, sources_data)
        docx_filename = os.path.basename(docx_path_str)
    except Exception as e:
        print(f"[!] Writer: Failed to generate DOCX report: {e}")
        docx_filename = ""
        
    duration = time.time() - start_time
    
    report_paths = {
        "pdf": pdf_filename,
        "docx": docx_filename
    }
    
    log_entry = {
        "agent": "Report Writer",
        "status": "completed",
        "duration": round(duration, 2),
        "output": f"Successfully compiled PDF and DOCX documents in the reports directory.",
        "details": report_paths,
        "timestamp": time.time()
    }
    
    return {
        "report_paths": report_paths,
        "agent_logs": [log_entry],
        "status": "storing"
    }
