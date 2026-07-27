import uuid
import logging
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.config import REPORTS_DIR, STATIC_DIR, TEMPLATES_DIR, LOGS_DIR, HOST, PORT
from backend.schemas import ResearchRequest, ResearchResponse, StatusResponse
from database import db
from graphs.workflow import research_graph

# Setup logging
log_file = LOGS_DIR / "app.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(str(log_file)),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("backend.main")

app = FastAPI(
    title="AI Research Team using Multi-Agent Systems",
    description="A production-ready FastAPI-based backend running LangGraph swarms."
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
try:
    db.init_db()
    logger.info("SQLite database verified/initialized.")
except Exception as e:
    logger.error(f"Failed to initialize SQLite database: {e}")

# Expose static assets and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

def run_research_workflow(session_id: str, topic: str):
    """
    Runs the LangGraph research state machine asynchronously in the background.
    """
    logger.info(f"[{session_id}] Commencing multi-agent research workflow for topic: '{topic}'")
    
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
        # Run graph
        final_state = research_graph.invoke(initial_state)
        logger.info(f"[{session_id}] Research graph completed successfully with status: {final_state.get('status')}")
    except Exception as e:
        logger.error(f"[{session_id}] LangGraph orchestration exception: {e}", exc_info=True)
        # Update session status as failed in database
        try:
            db.update_session_status(session_id, "failed")
        except Exception as db_err:
            logger.error(f"[{session_id}] Failed to save failure state to database: {db_err}")

# HTML Homepage Route
@app.get("/", response_class=HTMLResponse)
def get_homepage():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="frontend templates/index.html not found")
    return FileResponse(str(index_file))

# Endpoint: GET /api/config
@app.get("/api/config")
def get_config_status():
    from backend.config import GROQ_API_KEY, TAVILY_API_KEY, DEMO_MODE
    return {
        "demo_mode": DEMO_MODE,
        "groq_configured": bool(GROQ_API_KEY),
        "tavily_configured": bool(TAVILY_API_KEY),
        "database": "SQLite + ChromaDB fallback"
    }


# Endpoint: POST /research
@app.post("/research", response_model=ResearchResponse)
def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Initiates a new multi-agent research session.
    Fires off the LangGraph loop in the background and returns a session token.
    """
    session_id = str(uuid.uuid4())
    topic = request.topic.strip()
    
    logger.info(f"Creating research session {session_id} for topic: '{topic}'")
    
    try:
        db.create_session(session_id, topic)
    except Exception as e:
        logger.error(f"Failed to create session record: {e}")
        raise HTTPException(status_code=500, detail="Database write error.")
        
    # Schedule background execution of LangGraph
    background_tasks.add_task(run_research_workflow, session_id, topic)
    
    return ResearchResponse(
        session_id=session_id,
        topic=topic,
        status="planning"
    )

# Endpoint: GET /status/{id}
@app.get("/status/{id}", response_model=StatusResponse)
def get_research_status(id: str):
    """
    Returns the real-time execution status, logs, timeline, and results of a research task.
    """
    session = db.get_session(id)
    if not session:
        raise HTTPException(status_code=404, detail="Research session not found")
    return StatusResponse(**session)

# Endpoint: GET /history
@app.get("/history")
def get_research_history():
    """
    Lists historical research sessions sorted by date.
    """
    try:
        sessions = db.get_all_sessions()
        return sessions
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Database read error.")

# Endpoint: GET /api/stats
@app.get("/api/stats")
def get_dashboard_stats():
    """
    Computes summary stats from SQLite for the dashboard.
    """
    import json
    from memory.vector_db import CHROMA_AVAILABLE
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        # 1. Total Briefs (completed sessions)
        cursor.execute("SELECT COUNT(*) FROM research_sessions WHERE status = 'completed'")
        total_briefs = cursor.fetchone()[0]
        
        # 2. Avg Confidence Score
        cursor.execute("SELECT AVG(confidence_score) FROM research_sessions WHERE status = 'completed'")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # 3. Total references indexed
        cursor.execute("SELECT sources_data FROM research_sessions WHERE status = 'completed'")
        rows = cursor.fetchall()
        total_sources = 0
        for row in rows:
            if row[0]:
                try:
                    src = json.loads(row[0])
                    total_sources += len(src.get("papers", [])) + len(src.get("web_sources", []))
                except Exception:
                    pass
                    
        conn.close()
        
        return {
            "total_briefs": total_briefs,
            "avg_confidence": round(avg_confidence, 1),
            "total_sources": total_sources,
            "chroma_status": "Active" if CHROMA_AVAILABLE else "Disabled"
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {
            "total_briefs": 0,
            "avg_confidence": 0.0,
            "total_sources": 0,
            "chroma_status": "Error"
        }

# Endpoint: GET /download/pdf/{id}
@app.get("/download/pdf/{id}")
def download_pdf_report(id: str):
    """
    Downloads the compiled PDF file of the research session.
    """
    session = db.get_session(id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    pdf_path = session.get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=400, detail="PDF report was not generated for this session")
        
    file_path = REPORTS_DIR / pdf_path
    if not file_path.exists():
        logger.error(f"PDF file not found in filesystem: {file_path}")
        raise HTTPException(status_code=404, detail="PDF report file does not exist on disk")
        
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=pdf_path
    )

# Endpoint: GET /download/docx/{id}
@app.get("/download/docx/{id}")
def download_docx_report(id: str):
    """
    Downloads the compiled Word docx file of the research session.
    """
    session = db.get_session(id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    docx_path = session.get("docx_path")
    if not docx_path:
        raise HTTPException(status_code=400, detail="Word report was not generated for this session")
        
    file_path = REPORTS_DIR / docx_path
    if not file_path.exists():
        logger.error(f"Word file not found in filesystem: {file_path}")
        raise HTTPException(status_code=404, detail="Word report file does not exist on disk")
        
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=docx_path
    )

# Search indexed memories semantic search endpoint
@app.post("/memory/search")
def search_vector_memory(query_req: dict):
    """
    Optional semantic query endpoint to search prior indexed documents.
    """
    from memory.vector_db import search_memories
    q = query_req.get("query", "")
    limit = query_req.get("limit", 3)
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    try:
        return search_memories(q, limit)
    except Exception as e:
        logger.error(f"Search memory error: {e}")
        raise HTTPException(status_code=500, detail="Memory search exception")

if __name__ == "__main__":
    import uvicorn
    print(f"Starting server locally on http://{HOST}:{PORT}")
    uvicorn.run("backend.main:app", host=HOST, port=int(PORT), reload=True)
