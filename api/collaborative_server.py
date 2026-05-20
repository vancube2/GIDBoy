"""GIDBoy Collaborative Intelligence API.

This API returns ONE evolving intelligence narrative,
NOT modular agent outputs.
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.collaborative_engine import CollaborativeReasoningEngine
from llm_client import call_llm_api

app = FastAPI(
    title="GIDBoy Collaborative Intelligence OS",
    description="Working with you, not answering for you",
    version="4.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize collaborative engine
engine = CollaborativeReasoningEngine(llm_client=call_llm_api)


class CollaborateRequest(BaseModel):
    """Collaborative intelligence request."""
    query: str
    depth: Optional[str] = "full"  # 'quick', 'standard', 'deep'
    focus: Optional[str] = None  # e.g., 'opportunities', 'strategy', 'positioning'


class CollaborateResponse(BaseModel):
    """Collaborative intelligence response - ONE evolving narrative."""
    query: str
    collaborative_session: Dict[str, Any]
    reasoning_summary: str


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "GIDBoy Collaborative Intelligence OS",
        "version": "4.0.0",
        "description": "Working with you, not answering for you",
        "philosophy": "Collaborative reasoning, not modular responses",
        "endpoints": ["/collaborate", "/health"]
    }


@app.get("/health")
def health():
    """Health check."""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "mode": "collaborative_intelligence"
    }


@app.post("/collaborate", response_model=CollaborateResponse)
def collaborate(request: CollaborateRequest):
    """
    Start a collaborative intelligence session.

    Returns ONE evolving reasoning narrative, NOT modular outputs.
    """
    # Execute collaborative reasoning
    result = engine.collaborate(request.query)

    # Extract reasoning summary
    session = result.get("collaborative_intelligence_session", {})
    reasoning_trail = session.get("reasoning_trail", [])

    reasoning_summary = "\n\n".join([
        f"[{step.get('stage', 'unknown').upper()}] {step.get('thought', '')}"
        for step in reasoning_trail
    ])

    return CollaborateResponse(
        query=request.query,
        collaborative_session=session,
        reasoning_summary=reasoning_summary
    )


# Vercel handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
