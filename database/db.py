import sqlite3
import json
import datetime
from pathlib import Path
from backend.config import DATABASE_DIR

DB_PATH = DATABASE_DIR / "research.db"

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if it does not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_sessions (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence_score REAL DEFAULT 0.0,
            summary_data TEXT,
            sources_data TEXT,
            agent_logs TEXT,
            pdf_path TEXT,
            docx_path TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_session(session_id: str, topic: str):
    """Creates a new research session with pending status."""
    now = datetime.datetime.now().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO research_sessions 
        (id, topic, status, confidence_score, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (session_id, topic, "planning", 0.0, now, now)
    )
    conn.commit()
    conn.close()

def update_session_status(session_id: str, status: str, agent_logs: str = None):
    """Updates the status and optionally execution logs of an ongoing research session."""
    now = datetime.datetime.now().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    if agent_logs:
        cursor.execute(
            """
            UPDATE research_sessions
            SET status = ?, agent_logs = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, agent_logs, now, session_id)
        )
    else:
        cursor.execute(
            """
            UPDATE research_sessions
            SET status = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, now, session_id)
        )
    conn.commit()
    conn.close()

def update_session_results(
    session_id: str, 
    status: str, 
    confidence_score: float, 
    summary_data: dict, 
    sources_data: dict, 
    agent_logs: list, 
    pdf_path: str, 
    docx_path: str
):
    """Saves final research results, confidence scores, logs, and generated report file paths."""
    now = datetime.datetime.now().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE research_sessions
        SET status = ?, confidence_score = ?, summary_data = ?, sources_data = ?, 
            agent_logs = ?, pdf_path = ?, docx_path = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            status, 
            confidence_score, 
            json.dumps(summary_data), 
            json.dumps(sources_data), 
            json.dumps(agent_logs), 
            pdf_path, 
            docx_path, 
            now, 
            session_id
        )
    )
    conn.commit()
    conn.close()

def get_session(session_id: str):
    """Retrieves a single research session by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM research_sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        result = dict(row)
        # Parse JSON fields
        if result.get("summary_data"):
            result["summary_data"] = json.loads(result["summary_data"])
        if result.get("sources_data"):
            result["sources_data"] = json.loads(result["sources_data"])
        if result.get("agent_logs"):
            result["agent_logs"] = json.loads(result["agent_logs"])
        return result
    return None

def get_all_sessions():
    """Retrieves all historical research sessions, ordered by creation date desc."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM research_sessions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    sessions = []
    for row in rows:
        result = dict(row)
        if result.get("summary_data"):
            result["summary_data"] = json.loads(result["summary_data"])
        if result.get("sources_data"):
            result["sources_data"] = json.loads(result["sources_data"])
        if result.get("agent_logs"):
            result["agent_logs"] = json.loads(result["agent_logs"])
        sessions.append(result)
    return sessions

# Initialize tables when importing db module
init_db()
print("Initialized SQLite database.")
