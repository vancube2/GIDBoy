"""GIDBoy API with Intent Classification - ONLY entry point.

This is the ONLY server file. All requests go through intent classification FIRST.
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.intent_classifier import IntentRouter, IntentClassifier, ConversationalResponder

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

# Initialize intent router
router = IntentRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []


class ChatResponse(BaseModel):
    intent: str
    confidence: float
    requires_research: bool
    response: str
    workflow: str


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
    return {"status": "healthy", "version": "4.1.0", "mode": "intent_classification"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint WITH intent classification.

    NEVER forces research on casual input.
    """
    result = router.route(request.message, request.conversation_history)

    return ChatResponse(
        intent=result["intent"],
        confidence=result["confidence"],
        requires_research=result["requires_research"],
        response=result.get("response") or "I'm here to help. What would you like to explore?",
        workflow=result["workflow"]
    )


@app.post("/collaborate")
def collaborate(request: ChatRequest):
    """
    Collaborative endpoint with proper intent routing.
    """
    classification = router.classifier.classify(
        request.message,
        request.conversation_history
    )

    intent = classification.intent.value

    # CASUAL / GREETING
    if intent in ["greeting", "casual_conversation"]:
        return {
            "mode": "conversational",
            "intent": intent,
            "confidence": classification.confidence,
            "response": router.responder.generate_casual_response(request.message),
            "note": "Natural conversation - no research forced"
        }

    # COLLABORATION
    if intent == "collaboration_inquiry":
        return {
            "mode": "collaborative",
            "intent": intent,
            "confidence": classification.confidence,
            "response": router.responder.generate_collaboration_response(request.message)
        }

    # AMBIGUOUS
    if intent == "ambiguous":
        return {
            "mode": "clarification",
            "intent": intent,
            "confidence": classification.confidence,
            "response": router.responder.generate_ambiguous_response(request.message)
        }

    # Only NOW consider research
    if classification.requires_research:
        return {
            "mode": "deep_research",
            "intent": intent,
            "confidence": classification.confidence,
            "status": "research_activated",
            "message": "Research workflow activated based on clear intent",
            "entities": classification.extracted_entities
        }

    # Default
    return {
        "mode": "conversational",
        "intent": intent,
        "confidence": classification.confidence,
        "response": "I'm here. What would you like to work on?"
    }


# Catch-all for any other path - ALWAYS classify intent
@app.api_route("/{path:path}", methods=["GET", "POST"])
def catch_all(path: str, request: Dict[str, Any] = None):
    """
    Catch-all that ALWAYS uses intent classification.

    Prevents any request from bypassing intent classification.
    """
    # Extract message from various possible input formats
    message = ""
    if request and isinstance(request, dict):
        message = request.get("message", "") or request.get("query", "")

    if not message:
        return {
            "error": "No message provided",
            "hint": "Use /chat endpoint with JSON body: {\"message\": \"your input\"}"
        }

    # Classify and route
    result = router.route(message)

    return {
        "intent": result["intent"],
        "confidence": result["confidence"],
        "requires_research": result["requires_research"],
        "response": result.get("response"),
        "workflow": result["workflow"],
        "note": "Intent classification applied"
    }


# Vercel handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
