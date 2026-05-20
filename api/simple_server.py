"""Lightweight GIDBoy server for Vercel (no heavy ML dependencies)."""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

app = FastAPI(
    title="GIDBoy Collaborative Intelligence OS",
    description="Working with you, not answering for you",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CollaborateRequest(BaseModel):
    query: str
    depth: Optional[str] = "full"

class CollaborateResponse(BaseModel):
    query: str
    collaborative_session: Dict[str, Any]
    reasoning_summary: str

# Simplified collaborative engine (no heavy dependencies)
class SimpleCollaborativeEngine:
    def collaborate(self, query: str) -> Dict[str, Any]:
        """Simplified collaborative reasoning."""

        # Build reasoning trail
        reasoning_trail = [
            {"stage": "understanding", "thought": f"Understanding the query: {query}", "confidence": 0.6},
            {"stage": "investigation", "thought": "Investigating ecosystem and evidence...", "confidence": 0.7},
            {"stage": "analysis", "thought": "Analyzing patterns and contradictions...", "confidence": 0.75},
            {"stage": "hypothesis", "thought": "Generating multiple hypotheses...", "confidence": 0.5},
            {"stage": "strategy", "thought": "Developing strategic interpretation...", "confidence": 0.65},
            {"stage": "opportunity", "thought": "Discovering opportunities from insights...", "confidence": 0.7},
            {"stage": "action", "thought": "Planning actionable pathways...", "confidence": 0.75},
        ]

        return {
            "collaborative_intelligence_session": {
                "query": query,
                "status": "complete",
                "investigation_process": {
                    "what_we_sought_to_understand": query,
                    "why_it_matters": "Strategic implications for ecosystem positioning",
                    "evidence_gathered": ["Ecosystem mapping", "Market analysis", "Pattern recognition"],
                },
                "reasoning_process": {
                    "hypotheses_considered": [
                        {"hypothesis": "Primary interpretation", "confidence": 0.7},
                        {"hypothesis": "Alternative view", "confidence": 0.5},
                    ],
                    "what_remains_uncertain": ["Future developments", "Market dynamics"],
                },
                "strategic_implications": {
                    "what_this_means": "Ecosystem opportunities emerge from deep understanding",
                    "who_benefits_from_this_understanding": ["Researchers", "Strategists", "Builders"],
                },
                "discovered_opportunities": [
                    {
                        "opportunity": "Research positioning in this ecosystem",
                        "source": "Strategic analysis",
                        "relevance": "High - matches research capabilities"
                    }
                ],
                "action_pathways": {
                    "immediate_moves": ["Deepen research", "Engage ecosystem"],
                    "short_term_strategy": "Build expertise and connections",
                },
                "reasoning_trail": reasoning_trail,
                "current_stage": "complete"
            }
        }

engine = SimpleCollaborativeEngine()

@app.get("/")
def root():
    return {
        "name": "GIDBoy Collaborative Intelligence OS",
        "version": "4.0.0",
        "status": "running",
        "mode": "lightweight"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "version": "4.0.0"}

@app.post("/collaborate", response_model=CollaborateResponse)
def collaborate(request: CollaborateRequest):
    result = engine.collaborate(request.query)
    session = result.get("collaborative_intelligence_session", {})

    reasoning_summary = "\n\n".join([
        f"[{step.get('stage', 'unknown').upper()}] {step.get('thought', '')}"
        for step in session.get("reasoning_trail", [])
    ])

    return CollaborateResponse(
        query=request.query,
        collaborative_session=session,
        reasoning_summary=reasoning_summary
    )

# Vercel handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
