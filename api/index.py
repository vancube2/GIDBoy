"""GIDBoy API v2 with Session-Aware Intent Classification.

Persistent workflow state management for collaborative intelligence.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from core.session_manager import session_manager, SessionState
from core.intent_classifier_v2 import SessionAwareIntentClassifier, IntentType

app = FastAPI(
    title="GIDBoy Collaborative Intelligence OS v2",
    description="Session-aware collaborative intelligence with persistent workflow state",
    version="5.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
from core.collaborative_engine import CollaborativeReasoningEngine
from llm_client import call_llm_api
from prompts import SYSTEM_PROMPT, MODES

classifier = SessionAwareIntentClassifier()
reasoning_engine = CollaborativeReasoningEngine(llm_client=call_llm_api)


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    session_state: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    intent: str
    confidence: float
    requires_research: bool
    response: str
    workflow: str
    session_id: str
    is_continuation: bool
    active_topic: Optional[str] = None
    workflow_stage: Optional[str] = None
    session_state: Optional[Dict[str, Any]] = None


class SessionContext(BaseModel):
    session_id: str
    active_topic: Optional[str]
    workflow_stage: str
    conversation_mode: str
    discovered_insights: List[str]
    message_count: int


@app.get("/")
def root():
    return {
        "name": "GIDBoy Collaborative Intelligence OS v2",
        "version": "5.1.0",
        "description": "Session-aware collaborative intelligence",
        "features": [
            "session_management",
            "persistent_workflows",
            "context_awareness",
            "research_continuity"
        ],
        "endpoint": "/chat"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "5.1.0",
        "mode": "session_aware"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return _chat_handler(request)

@app.post("/task", response_model=ChatResponse)
def task(request: ChatRequest):
    return _chat_handler(request)

def _chat_handler(request: ChatRequest):
    """
    Main chat endpoint with session-aware intent classification.

    Maintains persistent workflow state across conversations.
    """
    try:
        session = session_manager.get_or_create_session(
            session_id=request.session_id,
            user_id=request.user_id
        )
        # CRITICAL: Hydrate session from client-provided state for serverless continuity
        if request.session_state:
            session_manager.hydrate_session(session.session_id, request.session_state)

        # Build session state for classifier
        session_state = session_manager.get_session_summary(session.session_id)

        # Classify with session context
        classification = classifier.classify(
            request.message,
            request.conversation_history,
            session_state
        )

        # Generate response based on classification
        response_data = generate_response(
            request.message,
            classification,
            session,
            request.conversation_history
        )

        # Update session state
        session_manager.add_message(
            session.session_id,
            'user',
            request.message,
            classification.intent.value
        )

        # Handle different intents
        if classification.intent == IntentType.RESEARCH_REQUEST:
            # Initialize new research session
            session_manager.set_active_topic(
                session.session_id,
                request.message,
                "deep"
            )
            session_manager.transition_stage(session.session_id, "understanding")

        elif classification.intent in [IntentType.RESEARCH_CONTINUATION, IntentType.RESEARCH_DEEPEN]:
            # Continue existing research
            if classification.recommended_stage:
                session_manager.transition_stage(
                    session.session_id,
                    classification.recommended_stage
                )

        elif classification.intent == IntentType.COLLABORATION_INQUIRY:
            session.conversation_mode = "collaborative"

        # Save assistant response
        session_manager.add_message(
            session.session_id,
            'assistant',
            response_data['response']
        )

        # Get updated session state
        final_state = session_manager.get_session_summary(session.session_id)

        return ChatResponse(
            intent=classification.intent.value,
            confidence=classification.confidence,
            requires_research=classification.requires_research,
            response=response_data['response'],
            workflow=classification.suggested_behavior,
            session_id=session.session_id,
            is_continuation=classification.is_continuation,
            active_topic=final_state.get('active_topic'),
            workflow_stage=final_state.get('workflow_stage'),
            session_state=final_state
        )
    except Exception as e:
        import traceback
        print(f"[GIDBoy Error] {e}")
        traceback.print_exc()
        return ChatResponse(
            intent="error",
            confidence=0.0,
            requires_research=False,
            response="I encountered a system error. Please try again in a moment.",
            workflow="error",
            session_id=request.session_id or "unknown",
            is_continuation=False,
            active_topic=None,
            workflow_stage="error",
            session_state={}
        )


@app.get("/session/{session_id}")
def get_session(session_id: str):
    """Get current session state."""
    session = session_manager.get_session(session_id)
    if not session:
        return {"error": "Session not found"}, 404

    return session_manager.get_session_summary(session_id)


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    """Clear session state."""
    if session_id in session_manager._sessions:
        del session_manager._sessions[session_id]
        return {"status": "cleared"}
    return {"error": "Session not found"}, 404


def _build_simple_research_response(topic, result):
    parts = ["# Research: " + topic + "\n"]
    cr = result.get("collaborative_response", {})
    if "problem_understanding" in cr:
        parts.append("## Problem Understanding\n" + str(cr["problem_understanding"]) + "\n")
    if "investigation" in cr:
        parts.append("## Investigation\n" + str(cr["investigation"]) + "\n")
    if "strategic_implications" in cr:
        parts.append("## Strategic Implications\n" + str(cr["strategic_implications"]) + "\n")
    if "opportunities" in cr:
        parts.append("## Opportunities\n" + str(cr["opportunities"]) + "\n")
    if "action_pathways" in cr:
        parts.append("## Action Pathways\n" + str(cr["action_pathways"]) + "\n")
    return "\n".join(parts) if len(parts) > 1 else "Research on " + topic + " is in progress."


def generate_response(message: str, classification: Any,
                     session: SessionState, history: List[Dict]) -> Dict[str, Any]:
    """Generate contextual response based on classification."""

    # Get session context for response
    context = session_manager.generate_context_prompt(session.session_id)

    if classification.intent == IntentType.GREETING:
        return {
            "response": "Hey there! Ready to dig into some research? What would you like to explore?"
        }

    elif classification.intent == IntentType.CASUAL_CONVERSATION:
        if "how are you" in message.lower():
            return {
                "response": "Doing well, thanks! Always ready to dive into ecosystem research. What about you?"
            }
        return {
            "response": "I'm here when you're ready to dive into something. What ecosystem or topic should we explore?"
        }

    elif classification.intent == IntentType.COLLABORATION_INQUIRY:
        return {
            "response": """I'd love to collaborate! Here's how we can work together:

**What I can help with:**
• Deep research on crypto ecosystems, protocols, or markets
• Strategic analysis and opportunity discovery
• Content generation from original research
• Positioning strategy and execution planning

**How it works:**
1. Share what you're interested in or working on
2. I'll do deep investigation with structured reasoning
3. We'll discover opportunities and strategic implications together
4. Turn insights into actionable positioning

What area are you exploring? Or what project are you working on?"""
        }

    elif classification.intent == IntentType.RESEARCH_REQUEST:
        topic = session.active_topic or message
        try:
            context = session_manager.generate_context_prompt(session.session_id)
            result = reasoning_engine.collaborate(topic, memory_context=context)
            narrative = result.get("collaborative_response", {}).get("narrative", "")
            if not narrative:
                narrative = _build_simple_research_response(topic, result)
            insights = result.get("collaborative_response", {}).get("discovered_opportunities", [])
            for opp in insights:
                if isinstance(opp, dict) and opp.get("opportunity"):
                    session_manager.add_insight(session.session_id, opp["opportunity"], "opportunity")
            return {"response": narrative, "topic_set": True}
        except Exception as e:
            print(f"[Research Error] {e}")
            return {"response": f"I would be happy to research {topic}. Let me dive deep into this and provide comprehensive analysis."}

    elif classification.intent == IntentType.RESEARCH_CONTINUATION:
        topic = session.active_topic or "this topic"
        try:
            context = session_manager.generate_context_prompt(session.session_id)
            result = reasoning_engine.collaborate(topic, memory_context=context)
            narrative = result.get("collaborative_response", {}).get("narrative", "")
            if not narrative:
                narrative = _build_simple_research_response(topic, result)
            return {"response": narrative}
        except Exception as e:
            print(f"[Continuation Error] {e}")
            msg_lower = message.lower()
            if "problem" in msg_lower or "challenge" in msg_lower:
                return {"response": f"Let me identify the key problems and challenges with {topic}..."}
            elif "solution" in msg_lower or "solving" in msg_lower:
                return {"response": f"Let me map the ecosystem solutions for {topic}..."}
            else:
                return {"response": f"Continuing our investigation on {topic}. What aspect would you like to explore next?"}

    elif classification.intent == IntentType.RESEARCH_DEEPEN:
        topic = session.active_topic or message
        try:
            context = session_manager.generate_context_prompt(session.session_id)
            result = reasoning_engine.collaborate(topic, memory_context=context)
            narrative = result.get("collaborative_response", {}).get("narrative", "")
            if not narrative:
                narrative = _build_simple_research_response(topic, result)
            return {"response": narrative}
        except Exception as e:
            print(f"[Deepen Error] {e}")
            return {"response": f"Let me go deeper into {session.active_topic}. Elaborating on the key mechanisms and implications..."}

    elif classification.intent == IntentType.WORKFLOW_TRANSITION:
        return {
            "response": f"Moving into {classification.recommended_stage} phase. Let me analyze what we've discovered so far...",
            "stage": classification.recommended_stage
        }

    elif classification.intent == IntentType.AMBIGUOUS:
        # Check if we have active topic
        if session.active_topic:
            return {
                "response": f"I want to make sure I understand. Are you asking about {session.active_topic}? Or would you like to explore something new?"
            }
        return {
            "response": "I'd like to help! Could you clarify what you're looking for?\n\n• Research on a specific topic?\n• Help finding opportunities?\n• Strategic brainstorming?\n• Or just chatting?"
        }

    return {
        "response": "I'm here to help. What would you like to explore?"
    }


# Vercel handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
