from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import json
import hashlib
import tempfile
import os

@dataclass
class SessionState:
    session_id: str
    created_at: datetime
    last_updated: datetime
    active_topic: Optional[str] = None
    workflow_stage: str = "initial"
    conversation_mode: str = "conversational"
    research_depth: str = "surface"
    discovered_insights: List[str] = field(default_factory=list)
    key_findings: List[Dict[str, Any]] = field(default_factory=list)
    unresolved_questions: List[str] = field(default_factory=list)
    generated_hypotheses: List[str] = field(default_factory=list)
    strategic_implications: List[str] = field(default_factory=list)
    opportunity_targets: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_intent_history: List[str] = field(default_factory=list)
    pending_clarifications: List[str] = field(default_factory=list)
    current_research_focus: Optional[str] = None
    investigation_paths: List[str] = field(default_factory=list)
    completed_stages: List[str] = field(default_factory=list)
    next_recommended_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_updated"] = datetime.fromisoformat(data["last_updated"])
        return cls(**data)

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}
        self._session_timeout = timedelta(hours=24)
        self._persist_dir = os.environ.get("SESSION_PERSIST_DIR", os.path.join(tempfile.gettempdir(), "gidboy_sessions"))
        try:
            os.makedirs(self._persist_dir, exist_ok=True)
        except OSError:
            self._persist_dir = os.path.join(tempfile.gettempdir(), "gidboy_sessions")
            os.makedirs(self._persist_dir, exist_ok=True)
        self._load_all_sessions()

    def _session_file_path(self, session_id: str) -> str:
        safe_id = hashlib.sha256(session_id.encode()).hexdigest()[:16]
        return os.path.join(self._persist_dir, f"{safe_id}.json")

    def _save_session_to_disk(self, session: SessionState) -> None:
        try:
            filepath = self._session_file_path(session.session_id)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[SessionManager] Failed to persist session: {e}")

    def _load_session_from_disk(self, session_id: str) -> Optional[SessionState]:
        try:
            filepath = self._session_file_path(session_id)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                session = SessionState.from_dict(data)
                if datetime.now() - session.last_updated > self._session_timeout:
                    os.remove(filepath)
                    return None
                return session
        except Exception as e:
            print(f"[SessionManager] Failed to load session: {e}")
        return None

    def _load_all_sessions(self) -> None:
        try:
            for filename in os.listdir(self._persist_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(self._persist_dir, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        session = SessionState.from_dict(data)
                        if datetime.now() - session.last_updated <= self._session_timeout:
                            self._sessions[session.session_id] = session
                        else:
                            os.remove(filepath)
                    except Exception:
                        continue
        except Exception:
            pass

    def get_or_create_session(self, session_id: Optional[str] = None, user_id: Optional[str] = None) -> SessionState:
        if session_id:
            session = self._sessions.get(session_id)
            if session:
                if datetime.now() - session.last_updated > self._session_timeout:
                    del self._sessions[session_id]
                    return self.get_or_create_session(None, user_id)
                session.last_updated = datetime.now()
                self._save_session_to_disk(session)
                return session
            session = self._load_session_from_disk(session_id)
            if session:
                self._sessions[session_id] = session
                return session
        new_session_id = session_id or self._generate_session_id(user_id)
        session = SessionState(
            session_id=new_session_id,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        self._sessions[new_session_id] = session
        self._save_session_to_disk(session)
        return session

    def get_session(self, session_id: str) -> Optional[SessionState]:
        session = self._sessions.get(session_id)
        if session:
            if datetime.now() - session.last_updated > self._session_timeout:
                del self._sessions[session_id]
                filepath = self._session_file_path(session_id)
                if os.path.exists(filepath):
                    os.remove(filepath)
                return None
            session.last_updated = datetime.now()
            self._save_session_to_disk(session)
            return session
        session = self._load_session_from_disk(session_id)
        if session:
            self._sessions[session_id] = session
            return session
        return None

    def save_session(self, session: SessionState) -> None:
        session.last_updated = datetime.now()
        self._sessions[session.session_id] = session
        self._save_session_to_disk(session)

    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Optional[SessionState]:
        session = self.get_session(session_id)
        if not session:
            return None
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        session.last_updated = datetime.now()
        self._save_session_to_disk(session)
        return session

    def add_message(self, session_id: str, role: str, content: str, intent: Optional[str] = None) -> Optional[SessionState]:
        session = self.get_session(session_id)
        if not session:
            return None
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "intent": intent
        }
        session.conversation_history.append(message)
        if len(session.conversation_history) > 50:
            session.conversation_history = session.conversation_history[-50:]
        if intent:
            session.user_intent_history.append(intent)
        self._save_session_to_disk(session)
        return session

    def transition_stage(self, session_id: str, new_stage: str) -> Optional[SessionState]:
        session = self.get_session(session_id)
        if not session:
            return None
        if session.workflow_stage != new_stage:
            session.completed_stages.append(session.workflow_stage)
            session.workflow_stage = new_stage
        self._save_session_to_disk(session)
        return session

    def add_insight(self, session_id: str, insight: str, category: Optional[str] = None) -> Optional[SessionState]:
        session = self.get_session(session_id)
        if not session:
            return None
        session.discovered_insights.append(insight)
        finding = {
            "insight": insight,
            "category": category or "general",
            "timestamp": datetime.now().isoformat()
        }
        session.key_findings.append(finding)
        self._save_session_to_disk(session)
        return session

    def add_hypothesis(self, session_id: str, hypothesis: str) -> Optional[SessionState]:
        session = self.get_session(session_id)
        if not session:
            return None
        session.generated_hypotheses.append(hypothesis)
        self._save_session_to_disk(session)
        return session

    def set_active_topic(self, session_id: str, topic: str, research_depth: str = "surface") -> Optional[SessionState]:
        session = self.get_session(session_id)
        if not session:
            return None
        if session.active_topic and session.active_topic != topic:
            session.investigation_paths.append(f"Previous: {session.active_topic}")
        session.active_topic = topic
        session.research_depth = research_depth
        session.workflow_stage = "understanding"
        session.conversation_mode = "research"
        self._save_session_to_disk(session)
        return session

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {}
        return {
            "active_topic": session.active_topic,
            "workflow_stage": session.workflow_stage,
            "conversation_mode": session.conversation_mode,
            "research_depth": session.research_depth,
            "key_insights_count": len(session.discovered_insights),
            "key_insights": session.discovered_insights[-5:],
            "unresolved_questions": session.unresolved_questions,
            "generated_hypotheses": session.generated_hypotheses[-3:],
            "completed_stages": session.completed_stages,
            "message_count": len(session.conversation_history)
        }

    def generate_context_prompt(self, session_id: str) -> str:
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
        if session.conversation_history:
            context_parts.append("Recent Conversation:")
            for msg in session.conversation_history[-4:]:
                prefix = "User" if msg["role"] == "user" else "GIDBoy"
                content = msg["content"][:200]
                context_parts.append(f"  {prefix}: {content}")
        return "\n".join(context_parts)

    def _generate_session_id(self, user_id: Optional[str] = None) -> str:
        timestamp = datetime.now().isoformat()
        user_component = user_id or "anon"
        hash_input = f"{user_component}_{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def hydrate_session(self, session_id: str, state: dict) -> "SessionState":
        """Hydrate session from client-provided state for serverless continuity."""
        session = self.get_session(session_id)
        if not session:
            return None
        if state.get("active_topic"):
            session.active_topic = state["active_topic"]
        if state.get("workflow_stage"):
            session.workflow_stage = state["workflow_stage"]
        if state.get("conversation_mode"):
            session.conversation_mode = state["conversation_mode"]
        if state.get("research_depth"):
            session.research_depth = state["research_depth"]
        if state.get("discovered_insights"):
            session.discovered_insights = list(state["discovered_insights"])
        if state.get("unresolved_questions"):
            session.unresolved_questions = list(state["unresolved_questions"])
        if state.get("generated_hypotheses"):
            session.generated_hypotheses = list(state["generated_hypotheses"])
        if state.get("completed_stages"):
            session.completed_stages = list(state["completed_stages"])
        if state.get("conversation_history"):
            existing = {m.get("timestamp", ""): True for m in session.conversation_history}
            for msg in state["conversation_history"]:
                ts = msg.get("timestamp", "")
                if ts and ts not in existing:
                    session.conversation_history.append(msg)
            if len(session.conversation_history) > 50:
                session.conversation_history = session.conversation_history[-50:]
        session.last_updated = datetime.now()
        self._save_session_to_disk(session)
        return session
    def cleanup_expired_sessions(self) -> int:
        now = datetime.now()
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session.last_updated > self._session_timeout
        ]
        for sid in expired:
            del self._sessions[sid]
            filepath = self._session_file_path(sid)
            if os.path.exists(filepath):
                os.remove(filepath)
        return len(expired)

session_manager = SessionManager()
