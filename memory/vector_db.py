import os
import sqlite3
from pathlib import Path
from backend.config import DATABASE_DIR

# Check if ChromaDB is available
CHROMA_AVAILABLE = False
chroma_client = None
collection = None

try:
    import chromadb
    from chromadb.config import Settings
    
    chroma_dir = DATABASE_DIR / "chroma"
    chroma_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize persistent client
    chroma_client = chromadb.PersistentClient(path=str(chroma_dir))
    # Create or get collection
    collection = chroma_client.get_or_create_collection(
        name="research_memories",
        metadata={"hnsw:space": "cosine"}
    )
    CHROMA_AVAILABLE = True
    print("[SUCCESS] ChromaDB persistent memory index initialized.")
except Exception as e:
    print(f"[!] ChromaDB initialization failed: {e}. Using SQLite keyword memory fallback.")

# SQLite Fallback Setup
DB_PATH = DATABASE_DIR / "research.db"

def init_sqlite_memory_table():
    """Initializes the SQLite fallback memory table."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_memories (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT
        )
    """)
    conn.commit()
    conn.close()

# Always initialize the SQLite table just in case we need it or fallback is active
init_sqlite_memory_table()

def index_research(session_id: str, topic: str, content: str, metadata: dict = None):
    """
    Stores research findings in ChromaDB (if available) or the SQLite memory table.
    """
    import json
    meta = metadata or {}
    meta.update({"session_id": session_id, "topic": topic})
    
    # 1. Store in ChromaDB if available
    if CHROMA_AVAILABLE and collection is not None:
        try:
            # Clean metadata to contain only string/int/float for Chroma compatibility
            clean_meta = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)
                    
            collection.add(
                documents=[content],
                metadatas=[clean_meta],
                ids=[session_id]
            )
            print(f"[SUCCESS] Indexed research session in ChromaDB collection.")
        except Exception as e:
            print(f"[!] ChromaDB index error: {e}. Falling back to SQLite storage.")
            save_to_sqlite_memory(session_id, topic, content, meta)
    else:
        save_to_sqlite_memory(session_id, topic, content, meta)

def save_to_sqlite_memory(session_id: str, topic: str, content: str, metadata: dict):
    """Fallback: Saves research memory to the SQLite database."""
    import json
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO research_memories (id, session_id, topic, content, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, session_id, topic, content, json.dumps(metadata))
        )
        conn.commit()
        conn.close()
        print(f"[SUCCESS] Indexed research session in SQLite fallback memory table.")
    except Exception as e:
        print(f"[ERROR] Failed to write SQLite fallback memory: {e}")

def search_memories(query: str, n_results: int = 3) -> list:
    """
    Queries indexed research databases for semantic matches.
    """
    results = []
    
    # 1. Try ChromaDB
    if CHROMA_AVAILABLE and collection is not None:
        try:
            chroma_res = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Formulate standard output format
            if chroma_res and chroma_res.get("documents"):
                docs = chroma_res["documents"][0]
                metas = chroma_res["metadatas"][0]
                ids = chroma_res["ids"][0]
                distances = chroma_res.get("distances", [[0]*n_results])[0]
                
                for doc, meta, doc_id, dist in zip(docs, metas, ids, distances):
                    results.append({
                        "session_id": doc_id,
                        "topic": meta.get("topic", ""),
                        "content": doc,
                        "score": round(float(1 - dist), 2) # Cosine similarity score
                    })
                return results
        except Exception as e:
            print(f"[!] ChromaDB query failed: {e}. Using SQLite keyword search.")
            
    # 2. SQLite Keyword Fallback Search
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Tokenize query for search terms
        words = [f"%{w.strip()}%" for w in query.split() if len(w.strip()) > 2]
        if not words:
            words = [f"%{query}%"]
            
        # SQL search construction
        where_clauses = " OR ".join(["content LIKE ?" for _ in words] + ["topic LIKE ?" for _ in words])
        sql = f"SELECT * FROM research_memories WHERE {where_clauses} LIMIT ?"
        params = words + words + [n_results]
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            results.append({
                "session_id": row["session_id"],
                "topic": row["topic"],
                "content": row["content"],
                "score": 0.85 # Fallback static score
            })
    except Exception as e:
        print(f"[ERROR] SQLite memory query error: {e}")
        
    return results
