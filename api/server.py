"""GIDBoy FastAPI server with LangGraph workflow integration."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Import agents and workflow
from workflows.research_workflow import create_workflow
from memory.vector_store import create_vector_store
from llm_client import call_llm_api

# Create FastAPI app
app = FastAPI(
    title="GIDBoy Intelligence OS",
    description="Collaborative research and opportunity intelligence system",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector store
vector_store = create_vector_store(
    collection_name="gidboy_memory",
    persist_dir="./data/chroma_db"
)

# Initialize workflow
workflow = create_workflow(
    llm_client=call_llm_api,
    vector_store=vector_store
)


class ResearchRequest(BaseModel):
    """Research request model."""
    query: str
    mode: Optional[str] = "research"
    deep_mode: Optional[bool] = True  # Run full workflow
    include_opportunities: Optional[bool] = True
    include_content: Optional[bool] = True
    include_execution: Optional[bool] = True


class ResearchResponse(BaseModel):
    """Research response model."""
    query: str
    mode: str
    status: str
    research: Dict[str, Any]
    opportunities: Optional[List[Dict[str, Any]]] = None
    content: Optional[Dict[str, Any]] = None
    execution: Optional[Dict[str, Any]] = None
    reasoning: List[str]


class QuickResearchRequest(BaseModel):
    """Quick research request (research only)."""
    query: str


class OpportunityRequest(BaseModel):
    """Opportunity discovery request."""
    query: str
    research_summary: Optional[Dict[str, Any]] = None


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "GIDBoy Intelligence OS",
        "version": "3.0.0",
        "description": "Collaborative research and opportunity intelligence",
        "endpoints": [
            "/research",
            "/research/quick",
            "/opportunities",
            "/health",
            "/memory/stats"
        ]
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "vector_store": vector_store.get_collection_stats()
    }


@app.post("/research", response_model=ResearchResponse)
def full_research(request: ResearchRequest):
    """
    Execute full research workflow with all agents.

    This runs the complete intelligence pipeline:
    1. Memory retrieval
    2. Deep research investigation
    3. Opportunity discovery
    4. Content generation
    5. Execution planning
    6. Memory storage
    """
    result = workflow.run(
        query=request.query,
        mode=request.mode
    )

    output = result.get("output", {})

    return ResearchResponse(
        query=request.query,
        mode=request.mode,
        status=result.get("status", "unknown"),
        research=output.get("research", {}),
        opportunities=output.get("opportunities", []) if request.include_opportunities else None,
        content=output.get("content", {}) if request.include_content else None,
        execution=output.get("execution", {}) if request.include_execution else None,
        reasoning=result.get("reasoning", [])
    )


@app.post("/research/quick")
def quick_research(request: QuickResearchRequest):
    """
    Quick research endpoint (research agent only).

    Faster response, ideal for initial exploration.
    """
    research = workflow.run_research_only(request.query)

    return {
        "query": request.query,
        "research": research,
        "status": "completed"
    }


@app.post("/opportunities")
def discover_opportunities(request: OpportunityRequest):
    """
    Discover opportunities based on research.

    If research_summary is provided, uses that context.
    Otherwise, runs research first.
    """
    if request.research_summary:
        opportunities = workflow.run_opportunities_only(
            query=request.query,
            research=request.research_summary
        )
    else:
        # Run full workflow
        result = workflow.run(query=request.query, mode="opportunity")
        opportunities = result.get("output", {}).get("opportunities", [])

    return {
        "query": request.query,
        "opportunities": opportunities,
        "count": len(opportunities)
    }


@app.get("/memory/search")
def search_memory(query: str, n: int = 3):
    """Search memory for relevant past research."""
    results = vector_store.similarity_search(query, k=n)
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


@app.get("/memory/stats")
def memory_stats():
    """Get memory statistics."""
    return vector_store.get_collection_stats()


@app.get("/agents")
def list_agents():
    """List available agents and their descriptions."""
    return {
        "agents": [
            {
                "name": "Research",
                "description": "Deep investigation, ecosystem mapping, hypothesis generation",
                "triggers": ["research", "analyze", "investigate", "understand"]
            },
            {
                "name": "Opportunity",
                "description": "Discovers jobs, grants, DAOs, strategic opportunities",
                "triggers": ["opportunity", "grant", "job", "funding", "position"]
            },
            {
                "name": "Content",
                "description": "Converts intelligence into authority-building content",
                "triggers": ["content", "thread", "post", "article", "write"]
            },
            {
                "name": "Execution",
                "description": "Turns intelligence into applications and outreach",
                "triggers": ["execute", "apply", "email", "outreach", "draft"]
            },
            {
                "name": "Memory",
                "description": "Preserves and retrieves long-term intelligence",
                "triggers": ["memory", "remember", "recall", "previous"]
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
