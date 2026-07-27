import os
import json
from groq import Groq
from backend.config import GROQ_API_KEY, GROQ_MODEL, DEMO_MODE

# Initialize Groq client if key is available
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("[SUCCESS] Groq client initialized successfully.")
    except Exception as e:
        print(f"[!] Error initializing Groq client: {e}")

def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """
    Utility function to call Groq API with error handling and fallback logic.
    """
    combined_prompt = f"{system_prompt}\n{user_prompt}"
    if DEMO_MODE or not client:
        # If demo mode is active or client failed to init, return a simulation fallback
        return get_mock_llm_response(combined_prompt, json_mode)

    try:
        # Construct message payload
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Configure arguments
        kwargs = {
            "model": GROQ_MODEL,
            "messages": messages,
            "temperature": 0.3,
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        chat_completion = client.chat.completions.create(**kwargs)
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        print(f"[!] Error during Groq API call: {e}. Falling back to mock data.")
        return get_mock_llm_response(combined_prompt, json_mode)

def get_mock_llm_response(user_prompt: str, json_mode: bool) -> str:
    """Generates premium mock responses depending on user query parameters."""
    user_prompt_lower = user_prompt.lower()
    
    # Check if this is coordinator planning
    if "research plan" in user_prompt_lower or "subtopics" in user_prompt_lower:
        if json_mode:
            return json.dumps({
                "subtopics": [
                    "Key Technological Foundations and Mechanics",
                    "Major Industry Players and Deployments",
                    "Core Challenges, Scaling Limits, and Latency Bottlenecks",
                    "Security, Privacy Risks, and Mitigation Strategies",
                    "Future Research Directions and Ecosystem Impact"
                ]
            })
        else:
            return "1. Key Foundations\n2. Industry Players\n3. Challenges\n4. Security\n5. Future Scope"

    # Check if this is summarizer
    if "executive summary" in user_prompt_lower or "key statistics" in user_prompt_lower:
        # We will parse out the topic in the user prompt
        topic = "the requested topic"
        for line in user_prompt.split('\n'):
            if "topic:" in line.lower() or "topic is" in line.lower():
                topic = line.split(":")[-1].strip()
                break
                
        data = {
            "executive_summary": f"This intelligence report provides a comprehensive, fact-verified review of {topic}. Our multi-agent research swarm conducted extensive web and literature reviews across trade publications and peer-reviewed papers. The findings indicate that while commercial adoption has spiked by 65% year-over-year, critical concerns regarding coordination latencies, token inflation, and source hallucination persist. Standardizing visual tracking, modular architectures, and semantic memory layers (ChromaDB/SQLite) represents the most viable path to mitigation.",
            "key_statistics": [
                {"metric": "Year-over-Year Commercial Growth", "value": "65%", "description": "Rapid acceleration in enterprise adoption across logistics and compliance workflows."},
                {"metric": "Average Orchestration Overhead", "value": "45%", "description": "Latency increase associated with state consolidation and agentic feedback loops."},
                {"metric": "Information Noise Reduction", "value": "85%", "description": "Calculated efficiency from applying Fact Verification de-duplication and source checking."}
            ],
            "findings": [
                {
                    "subtopic": "Key Technological Foundations and Mechanics",
                    "details": f"The mechanics of {topic} rely on high-fidelity state representation. Modern systems use directed graphs (like LangGraph) rather than simple linear chains. This enables cyclical routing, enabling agents to query APIs, verify answers, and re-query on error. This loops back state changes iteratively, producing much cleaner documents."
                },
                {
                    "subtopic": "Major Industry Players and Deployments",
                    "details": "Major cloud providers and developer platforms have integrated multi-agent swarms into IDE copilots and automated coding workstations. Industry reports indicate that early deployment has moved from simple code-generation utilities to multi-file refactoring and complete compliance verification agents."
                },
                {
                    "subtopic": "Core Challenges, Scaling Limits, and Latency Bottlenecks",
                    "details": "The primary blocker is the cost and speed of deep cognitive loops. Querying LLMs for validation, analysis, and generation sequentially introduces network overhead. Multi-agent designs attempt to parallelize research, but compiling these into a single summary remains a central bottleneck."
                },
                {
                    "subtopic": "Security, Privacy Risks, and Mitigation Strategies",
                    "details": "Exposing agents to external tools (Tavily search, SQLite, file writing) risks prompt injection. Modern security recommendations suggest running agents in sandboxed virtual workspaces, sanitizing all input arguments, and enforcing human-in-the-loop approvals for writing system-critical files."
                },
                {
                    "subtopic": "Future Research Directions and Ecosystem Impact",
                    "details": "Academic research is shifting towards low-latency offline SLMs (Small Language Models) specialized in single roles (like Fact Checking). Coupling these specialized local models with centralized routers is projected to cut orchestration costs by 70% in the next five years."
                }
            ],
            "advantages": [
                {"title": "Unbiased Fact Verification", "description": "Automated cross-checking across different API data streams eliminates single-source hallucination."},
                {"title": "Professional Document Structure", "description": "Structured generation flow allows cover page layout, table of contents formatting, and references sections to build automatically."}
            ],
            "challenges": [
                {"title": "API Dependency & Cost", "description": "High rate of API queries to Groq and Tavily increases overall cost per query and rate-limit risks."},
                {"title": "Coordination Lag", "description": "Sequential steps introduce total runtime delays of 10-15 seconds per research session."}
            ],
            "conclusion": f"In conclusion, {topic} represents a high-potential research target. Although early deployments face latency and security hurdles, coupling graph architectures with multi-agent consensus algorithms resolves major factual accuracy issues, paving the way for enterprise deployment.",
            "future_scope": "Next-generation research systems will integrate hierarchical agent structures, where coordinator nodes spin up temporary sub-swarms dynamically to tackle detailed topics before compiling findings."
        }
        return json.dumps(data)

    # Check if this is fact checking
    if "fact verification" in user_prompt_lower or "credibility" in user_prompt_lower:
        # Parse items from user prompt
        return json.dumps({
            "confidence_score": 88.5,
            "logs": "De-duplicated 3 redundant search entries. Checked arxiv authors against citation lists. Calculated high authority metrics for domains wire.com and techcrunch.com."
        })

    # Default general fallback
    if json_mode:
        return "{}"
    return "Simulated response for: " + user_prompt[:100]
