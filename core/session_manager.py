"""GIDBoy Session Management - Persistent Workflow State.

Manages active research sessions, workflow continuity, and conversational context.
Never loses track of ongoing investigations.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import json
import hashlib


@dataclass
class SessionState:
    """Complete session state for active workflows."""

    # Session Identity
    session_id: str
    created_at: datetime
    last_updated: datetime

    # Active Context
    active_topic: Optional[str] = None
    workflow_stage: str = "initial"  # initial, understanding, investigation, analysis, synthesis, complete
    conversation_mode: str = "conversational"  # conversational, research, collaborative
    research_depth: str = "surface"  # surface, deep, comprehensive

    # Accumulated Knowledge
    discovered_insights: List[str] = field(default_factory=list)
    key_findings: List[Dict[str, Any]] = field(default_factory=list)
    unresolved_questions: List[str] = field(default_factory=list)
    generated_hypotheses: List[str] = field(default_factory=list)
    strategic_implications: List[str] = field(default_factory=list)
    opportunity_targets: List[Dict[str, Any]] = field(default_factory=list)

    # Conversation Context
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_intent_history: List[str] = field(default_factory=list)
    pending_clarifications: List[str] = field(default_factory=list)

    # Workflow Tracking
    current_research_focus: Optional[str] = None
    investigation_paths: List[str] = field(default_factory=list)
    completed_stages: List[str] = field(default_factory=list)
    next_recommended_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionState':
        """Deserialize state from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        return cls(**data)


class SessionManager:
    """Manages persistent session state across interactions."""

    def __init__(self):
        # In-memory session store (use Redis in production)
        self._sessions: Dict[str, SessionState] = {}
        self._session_timeout = timedelta(hours=24)

    def get_or_create_session(self, session_id: Optional[str] = None,
                              user_id: Optional[str] = None) -> SessionState:
        """Get existing session or create new one."""
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            session.last_updated = datetime.now()
            return session

        # Create new session
        new_session_id = session_id or self._generate_session_id(user_id)
        session = SessionState(
            session_id=new_session_id,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        self._sessions[new_session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve existing session."""
        session = self._sessions.get(session_id)
        if session:
            # Check for timeout
            if datetime.now() - session.last_updated > self._session_timeout:
                del self._sessions[session_id]
                return None
            session.last_updated = datetime.now()
        return session

    def save_session(self, session: SessionState) -> None:
        """Save session state."""
        session.last_updated = datetime.now()
        self._sessions[session.session_id] = session

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[SessionState]:
        """Update specific session fields."""
        session = self.get_session(session_id)
        if not session:
            return None

        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.last_updated = datetime.now()
        return session

    def add_message(self, session_id: str, role: str, content: str,
                    intent: Optional[str] = None) -> Optional[SessionState]:
        """Add message to session history."""
        session = self.get_session(session_id)
        if not session:
            return None

        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'intent': intent
        }
        session.conversation_history.append(message)

        # Keep only last 50 messages
        if len(session.conversation_history) > 50:
            session.conversation_history = session.conversation_history[-50:]

        if intent:
            session.user_intent_history.append(intent)

        return session

    def is_active_research_session(self, session_id: str) -> bool:
        """Check if session has active research in progress."""
        session = self.get_session(session_id)
        if not session:
            return False

        return (
            session.active_topic is not None or
            session.workflow_stage in ['investigation', 'analysis', 'synthesis'] or
            len(session.discovered_insights) > 0
        )

    def transition_stage(self, session_id: str, new_stage: str) -> Optional[SessionState]:
        """Transition workflow to new stage."""
        session = self.get_session(session_id)
        if not session:
            return None

        if session.workflow_stage != new_stage:
            session.completed_stages.append(session.workflow_stage)
            session.workflow_stage = new_stage

        return session

    def add_insight(self, session_id: str, insight: str,
                    category: Optional[str] = None) -> Optional[SessionState]:
        """Add discovered insight to session."""
        session = self.get_session(session_id)
        if not session:
            return None

        session.discovered_insights.append(insight)

        # Also add as structured finding
        finding = {
            'insight': insight,
            'category': category or 'general',
            'timestamp': datetime.now().isoformat()
        }
        session.key_findings.append(finding)

        return session

    def add_hypothesis(self, session_id: str, hypothesis: str) -> Optional[SessionState]:
        """Add generated hypothesis to session."""
        session = self.get_session(session_id)
        if not session:
            return None

        session.generated_hypotheses.append(hypothesis)
        return session

    def set_active_topic(self, session_id: str, topic: str,
                         research_depth: str = "surface") -> Optional[SessionState]:
        """Set or update active research topic."""
        session = self.get_session(session_id)
        if not session:
            return None

        # If changing topics, archive previous state
        if session.active_topic and session.active_topic != topic:
            session.investigation_paths.append(f"Previous: {session.active_topic}")

        session.active_topic = topic
        session.research_depth = research_depth
        session.workflow_stage = "understanding"
        session.conversation_mode = "research"

        return session

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of session state for context injection."""
        session = self.get_session(session_id)
        if not session:
            return {}

        return {
            'active_topic': session.active_topic,
            'workflow_stage': session.workflow_stage,
            'conversation_mode': session.conversation_mode,
            'research_depth': session.research_depth,
            'key_insights_count': len(session.discovered_insights),
            'key_insights': session.discovered_insights[-5:],  # Last 5
            'unresolved_questions': session.unresolved_questions,
            'generated_hypotheses': session.generated_hypotheses[-3:],  # Last 3
            'completed_stages': session.completed_stages,
            'message_count': len(session.conversation_history)
        }

    def generate_context_prompt(self, session_id: str) -> str:
        """Generate context-aware prompt prefix based on session state."""
        session = self.get_session(session_id)
        if not session:
            return ""

        context_parts = []

        if session.active_topic:
            context_parts.append(f"Active Research Topic: {session.active_topic}")

        if session.workflow_stage != "initial":
            context_parts.append(f"Current Stage: {session.workflow_stage}")

        if session.discovered_insights:
            context_parts.append("Key Insights So Far:")
            for insight in session.discovered_insights[-3:]:
                context_parts.append(f"  - {insight}")

        if session.unresolved_questions:
            context_parts.append("Questions to Address:")
            for q in session.unresolved_questions[:2]:
                context_parts.append(f"  - {q}")

        if session.generated_hypotheses:
            context_parts.append("Working Hypotheses:")
            for h in session.generated_hypotheses[-2:]:
                context_parts.append(f"  - {h}")

        return "\n".join(context_parts)

    def _generate_session_id(self, user_id: Optional[str] = None) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().isoformat()
        user_component = user_id or "anon"
        hash_input = f"{user_component}_{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions. Returns count removed."""
        now = datetime.now()
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session.last_updated > self._session_timeout
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


# Global session manager instance
session_manager = SessionManager()
