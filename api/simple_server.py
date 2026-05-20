"""Lightweight GIDBoy server for Vercel with Intent Classification.

This server PROPERLY classifies intent BEFORE any orchestration.
Never forces research on casual conversation.
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

app = FastAPI(
    title="GIDBoy Collaborative Intelligence OS",
    description="Context-aware, not keyword-triggered",
    version="4.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []


class ChatResponse(BaseModel):
    intent: str
    confidence: float
    requires_research: bool
    response: str
    workflow: str


# Import intent classifier
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.intent_classifier import IntentRouter, IntentClassifier, ConversationalResponder

router = IntentRouter()


@app.get("/")
def root():
    return {
        "name": "GIDBoy Collaborative Intelligence OS",
        "version": "4.1.0",
        "description": "Context-aware collaborative intelligence",
        "features": ["intent_classification", "conversational_mode", "deep_research"],
        "endpoint": "/chat"
    }


@app.get("/health")
def health():
    return {"status": "healthy", "version": "4.1.0"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint with proper intent classification.

    Classifies intent BEFORE any workflow activation.
    Never forces research on casual input.
    """
    # Route based on classified intent
    result = router.route(request.message, request.conversation_history)

    return ChatResponse(
        intent=result["intent"],
        confidence=result["confidence"],
        requires_research=result["requires_research"],
        response=result["response"] or "I'd be happy to research that for you. Let me investigate...",
        workflow=result["workflow"]
    )


@app.post("/collaborate")
def collaborate(request: ChatRequest):
    """
    Collaborative intelligence endpoint.

    Only activates deep research when intent classification
    determines it's appropriate.
    """
    # Classify first
    classification = router.classifier.classify(
        request.message,
        request.conversation_history
    )

    # If casual conversation, respond conversationally
    if classification.intent.value in ["greeting", "casual_conversation"]:
        return {
            "mode": "conversational",
            "intent": classification.intent.value,
            "confidence": classification.confidence,
            "response": router.responder.generate_casual_response(request.message),
            "note": "Research workflows only activate on clear research intent"
        }

    # If collaboration inquiry
    if classification.intent.value == "collaboration_inquiry":
        return {
            "mode": "collaborative",
            "intent": classification.intent.value,
            "confidence": classification.confidence,
            "response": router.responder.generate_collaboration_response(request.message),
            "next_steps": "Share what you're working on and I'll do deep research"
        }

    # If ambiguous, ask for clarification
    if classification.intent.value == "ambiguous":
        return {
            "mode": "clarification",
            "intent": classification.intent.value,
            "confidence": classification.confidence,
            "response": router.responder.generate_ambiguous_response(request.message),
            "suggestions": [
                "Research on a specific topic",
                "Opportunity search",
                "Strategic brainstorming",
                "Just chatting"
            ]
        }

    # Only NOW do we consider research
    if classification.requires_research:
        return {
            "mode": "deep_research",
            "intent": classification.intent.value,
            "confidence": classification.confidence,
            "status": "research_activated",
            "message": "Activating deep research workflow...",
            "entities_detected": classification.extracted_entities,
            "note": "This would trigger the full collaborative research engine"
        }

    # Default response
    return {
        "mode": "conversational",
        "intent": classification.intent.value,
        "confidence": classification.confidence,
        "response": "I'm here to help. What would you like to explore?"
    }


# Vercel handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
