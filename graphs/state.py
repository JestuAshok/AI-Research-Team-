from typing import Dict, List, Any, TypedDict, Annotated
import operator

def append_list(left: list, right: list) -> list:
    """Helper reducer to append list items instead of overwriting."""
    return left + right

class AgentState(TypedDict):
    """
    State representing the data passed between nodes in the LangGraph workflow.
    """
    session_id: str
    topic: str
    plan: List[str]
    raw_results: Annotated[List[Dict[str, Any]], append_list]
    verified_results: Annotated[List[Dict[str, Any]], append_list]
    summary: Dict[str, Any]
    confidence_score: float
    report_paths: Dict[str, str]
    agent_logs: Annotated[List[Dict[str, Any]], append_list]
    status: str
