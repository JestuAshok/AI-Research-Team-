from langgraph.graph import StateGraph, START, END
from graphs.state import AgentState

# Import nodes from our agents package
from agents.coordinator import coordinator_node
from agents.researcher import research_node
from agents.fact_checker import fact_checker_node
from agents.summarizer import summarizer_node
from agents.writer import writer_node
from agents.memory_agent import memory_node

# Initialize workflow with our typed state schema
workflow = StateGraph(AgentState)

# Define nodes
workflow.add_node("coordinator", coordinator_node)
workflow.add_node("researcher", research_node)
workflow.add_node("fact_checker", fact_checker_node)
workflow.add_node("summarizer", summarizer_node)
workflow.add_node("writer", writer_node)
workflow.add_node("memory", memory_node)

# Add linear routing connections
workflow.add_edge(START, "coordinator")
workflow.add_edge("coordinator", "researcher")
workflow.add_edge("researcher", "fact_checker")
workflow.add_edge("fact_checker", "summarizer")
workflow.add_edge("summarizer", "writer")
workflow.add_edge("writer", "memory")
workflow.add_edge("memory", END)

# Compile the execution graph
research_graph = workflow.compile()
print("[SUCCESS] Compiled LangGraph state graph.")
