from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="The research topic / query to analyze")

class ResearchResponse(BaseModel):
    session_id: str
    topic: str
    status: str

class AgentLogEntry(BaseModel):
    agent: str
    status: str
    duration: float
    output: str
    details: Any
    timestamp: float

class StatusResponse(BaseModel):
    id: str
    topic: str
    status: str
    confidence_score: float
    summary_data: Optional[Dict[str, Any]] = None
    sources_data: Optional[Dict[str, Any]] = None
    agent_logs: Optional[List[Dict[str, Any]]] = None
    pdf_path: Optional[str] = None
    docx_path: Optional[str] = None
    created_at: str
    updated_at: str

class MemorySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 3
