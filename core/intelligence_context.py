"""GIDBoy Collaborative Intelligence Context.

This is the HEART of GIDBoy - a shared reasoning space where:
- Investigation flows into reasoning
- Reasoning reveals opportunities
- Opportunities suggest positioning
- Positioning enables action

NOT modular agents. One continuous collaborative process.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class ReasoningStep:
    """A single step in the collaborative reasoning process."""
    stage: str  # 'investigation', 'analysis', 'hypothesis', 'opportunity', 'positioning', 'action'
    thought: str
    evidence: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 0.5  # 0-1, evolves as reasoning develops


@dataclass
class IntelligenceContext:
    """
    Shared reasoning context that evolves throughout the collaborative process.

    This is NOT a container for agent outputs.
    This is a living reasoning space that deepens over time.
    """
    # Original query
    query: str

    # Understanding that evolves
    problem_understanding: str = ""
    why_it_matters: str = ""
    who_is_affected: List[str] = field(default_factory=list)
    key_assumptions: List[str] = field(default_factory=list)

    # Context that gets mapped
    ecosystem_map: Dict[str, Any] = field(default_factory=dict)
    key_actors: List[Dict[str, Any]] = field(default_factory=list)
    market_dynamics: str = ""
    historical_context: str = ""

    # Evidence and findings (accumulates)
    evidence_gathered: List[Dict[str, Any]] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    data_points: List[Dict[str, Any]] = field(default_factory=list)

    # Hypotheses (multiple, competing)
    hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    current_hypothesis: Optional[str] = None

    # Uncertainties (NEVER hidden)
    known_unknowns: List[str] = field(default_factory=list)
    information_gaps: List[str] = field(default_factory=list)

    # Contradictions and tensions
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    competing_interpretations: List[str] = field(default_factory=list)

    # Strategic interpretation (emerges naturally)
    strategic_implications: str = ""
    first_order_effects: List[str] = field(default_factory=list)
    second_order_effects: List[str] = field(default_factory=list)
    third_order_effects: List[str] = field(default_factory=list)

    # Opportunities (discovered through reasoning, not generated)
    discovered_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    who_would_value_this: List[str] = field(default_factory=list)
    positioning_angles: List[str] = field(default_factory=list)

    # Action pathways (emerge from strategy)
    actionable_pathways: List[Dict[str, Any]] = field(default_factory=list)
    immediate_moves: List[str] = field(default_factory=list)
    short_term_strategy: str = ""
    medium_term_strategy: str = ""

    # Content that emerges from insight (not generated)
    core_insights: List[str] = field(default_factory=list)
    narrative_threads: List[str] = field(default_factory=list)

    # Reasoning trail (the actual thinking process)
    reasoning_trail: List[ReasoningStep] = field(default_factory=list)

    # Current stage
    current_stage: str = "initializing"  # evolves: understanding → investigation → analysis → discovery → strategy → action

    # Conversation/memory
    previous_related_work: List[str] = field(default_factory=list)

    def add_reasoning_step(self, stage: str, thought: str, evidence: List[str] = None,
                          uncertainties: List[str] = None, contradictions: List[str] = None,
                          confidence: float = 0.5):
        """Add a reasoning step to the trail."""
        step = ReasoningStep(
            stage=stage,
            thought=thought,
            evidence=evidence or [],
            uncertainties=uncertainties or [],
            contradictions=contradictions or [],
            confidence=confidence
        )
        self.reasoning_trail.append(step)
        self.current_stage = stage

    def deepen_understanding(self, new_insight: str):
        """Deepen understanding - builds on previous."""
        if self.problem_understanding:
            self.problem_understanding += f"\n\nFurther: {new_insight}"
        else:
            self.problem_understanding = new_insight

    def add_hypothesis(self, hypothesis: str, evidence: List[str], confidence: float):
        """Add competing hypothesis - NOT replacing, adding."""
        self.hypotheses.append({
            "hypothesis": hypothesis,
            "evidence": evidence,
            "confidence": confidence,
            "status": "active"  # can become 'confirmed', 'rejected', 'merged'
        })

    def discover_opportunity(self, opportunity: str, source: str, relevance: str, action: str):
        """Opportunities emerge from findings, not generated generically."""
        self.discovered_opportunities.append({
            "opportunity": opportunity,
            "source": source,  # which finding/insight led to this
            "relevance": relevance,
            "action": action,
            "discovered_at": datetime.now().isoformat()
        })

    def get_reasoning_summary(self) -> str:
        """Get the reasoning trail as a narrative."""
        summary = []
        for step in self.reasoning_trail:
            summary.append(f"[{step.stage.upper()}] {step.thought}")
            if step.uncertainties:
                summary.append(f"  Uncertainties: {', '.join(step.uncertainties)}")
        return "\n\n".join(summary)

    def to_collaborative_response(self) -> Dict[str, Any]:
        """
        Convert to final response that feels like a collaborative session.
        NOT modular outputs. One evolving intelligence narrative.
        """
        return {
            "collaborative_session": {
                "query": self.query,
                "thinking_process": {
                    "how_we_understood": self.problem_understanding,
                    "what_we_investigated": self.evidence_gathered,
                    "hypotheses_considered": self.hypotheses,
                    "what_still_uncertain": self.known_unknowns,
                },
                "strategic_insight": {
                    "what_this_means": self.strategic_implications,
                    "who_benefits": self.who_would_value_this,
                    "positioning_angles": self.positioning_angles,
                },
                "discovered_opportunities": self.discovered_opportunities,
                "action_pathways": self.actionable_pathways,
                "reasoning_trail": [
                    {
                        "stage": step.stage,
                        "thought": step.thought,
                        "confidence": step.confidence
                    }
                    for step in self.reasoning_trail
                ],
                "current_stage": self.current_stage
            }
        }


class CollaborativeIntelligenceEngine:
    """
    Orchestrates the collaborative reasoning process.

    NOT a pipeline of agents.
    A continuous reasoning process that deepens understanding.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.context: Optional[IntelligenceContext] = None

    def start_collaboration(self, query: str) -> IntelligenceContext:
        """Begin a collaborative intelligence session."""
        self.context = IntelligenceContext(query=query)
        self.context.add_reasoning_step(
            stage="initializing",
            thought=f"Starting collaborative investigation of: {query}",
            confidence=1.0
        )
        return self.context

    def investigate(self) -> IntelligenceContext:
        """
        Investigation phase - not isolated, part of continuous reasoning.
        """
        ctx = self.context

        # Deepen understanding
        ctx.add_reasoning_step(
            stage="understanding",
            thought="First, what are we actually trying to understand? What are the underlying questions?",
            uncertainties=["What assumptions are we bringing?", "What do we not yet know?"]
        )

        # Map context
        ctx.add_reasoning_step(
            stage="context_mapping",
            thought="Mapping the ecosystem and key dynamics...",
            evidence=["Identifying key actors", "Understanding market structure"]
        )

        # Gather evidence
        ctx.add_reasoning_step(
            stage="investigation",
            thought="Gathering evidence and examining the landscape...",
            uncertainties=["What sources are reliable?", "What might we be missing?"]
        )

        return ctx

    def analyze_and_hypothesize(self) -> IntelligenceContext:
        """
        Analysis phase - generates multiple hypotheses, doesn't converge prematurely.
        """
        ctx = self.context

        ctx.add_reasoning_step(
            stage="analysis",
            thought="Now let's analyze what we've found. What patterns emerge? What contradictions exist?",
            evidence=ctx.key_findings,
            contradictions=ctx.contradictions if ctx.contradictions else ["Looking for tensions in the data..."]
        )

        ctx.add_reasoning_step(
            stage="hypothesis_generation",
            thought="Generating multiple hypotheses - not committing to one yet...",
            uncertainties=["Which hypothesis best explains the evidence?", "What would falsify each?"]
        )

        return ctx

    def discover_strategic_implications(self) -> IntelligenceContext:
        """
        Strategic interpretation - emerges from reasoning, not generated.
        """
        ctx = self.context

        ctx.add_reasoning_step(
            stage="strategic_interpretation",
            thought="What does this mean strategically? Who benefits? What shifts?",
            evidence=ctx.key_findings
        )

        return ctx

    def identify_opportunities(self) -> IntelligenceContext:
        """
        Opportunities emerge from strategic understanding, not generic lists.
        """
        ctx = self.context

        ctx.add_reasoning_step(
            stage="opportunity_discovery",
            thought="Based on these strategic insights, what opportunities emerge? Who would value this understanding?",
            evidence=[f"Found {len(ctx.discovered_opportunities)} opportunity pathways"]
        )

        return ctx

    def develop_action_pathways(self) -> IntelligenceContext:
        """
        Action pathways emerge naturally from opportunities.
        """
        ctx = self.context

        ctx.add_reasoning_step(
            stage="action_development",
            thought="Given these opportunities, what are the actionable pathways?",
            evidence=ctx.positioning_angles
        )

        return ctx

    def collaborate(self, query: str) -> Dict[str, Any]:
        """
        Full collaborative intelligence process.

        Returns a narrative that evolves, not modular outputs.
        """
        self.start_collaboration(query)

        # These aren't separate agents - they're deepening stages
        self.investigate()
        self.analyze_and_hypothesize()
        self.discover_strategic_implications()
        self.identify_opportunities()
        self.develop_action_pathways()

        # Final synthesis - collaborative session output
        return self.context.to_collaborative_response()
