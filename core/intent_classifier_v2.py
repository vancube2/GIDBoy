"""GIDBoy Intent Classification System v2 - Session-Aware.

Distinguishes between different interaction types WITH session context awareness.
Understands when to continue active workflows vs start new ones.
"""
from enum import Enum
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import re


class IntentType(Enum):
    """Classification of user intent."""
    GREETING = "greeting"
    CASUAL_CONVERSATION = "casual_conversation"
    COLLABORATION_INQUIRY = "collaboration_inquiry"
    RESEARCH_REQUEST = "research_request"
    RESEARCH_CONTINUATION = "research_continuation"
    RESEARCH_DEEPEN = "research_deepen"
    OPPORTUNITY_SEARCH = "opportunity_search"
    CONTENT_GENERATION = "content_generation"
    STRATEGIC_BRAINSTORMING = "strategic_brainstorming"
    EXECUTION_TASK = "execution_task"
    CLARIFICATION_REQUEST = "clarification_request"
    FOLLOW_UP_DISCUSSION = "follow_up_discussion"
    WORKFLOW_TRANSITION = "workflow_transition"
    AMBIGUOUS = "ambiguous"


@dataclass
class IntentClassification:
    """Result of intent classification."""
    intent: IntentType
    confidence: float
    requires_research: bool
    suggested_behavior: str
    extracted_entities: List[str]
    context_needs: List[str]
    is_continuation: bool = False
    recommended_stage: Optional[str] = None


class SessionAwareIntentClassifier:
    """
    Session-aware intent classifier.

    Understands:
    - When user is continuing an active research session
    - When to transition between workflow stages
    - When to maintain conversational continuity
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def classify(self, user_input: str,
                 conversation_history: List[Dict] = None,
                 session_state: Optional[Dict] = None) -> IntentClassification:
        """
        Classify user intent WITH session context.

        Session state helps determine if this is a continuation.
        """
        user_input_lower = user_input.lower().strip()
        conversation_history = conversation_history or []
        session_state = session_state or {}

        # Extract session context
        active_topic = session_state.get('active_topic')
        workflow_stage = session_state.get('workflow_stage', 'initial')
        conversation_mode = session_state.get('conversation_mode', 'conversational')
        has_insights = session_state.get('key_insights_count', 0) > 0

        # Stage 1: Check for CONTINUATION patterns first (if active session)
        if active_topic:
            continuation_result = self._check_continuation(
                user_input_lower, active_topic, workflow_stage, has_insights
            )
            if continuation_result:
                return continuation_result

        # Stage 2: Check for WORKFLOW TRANSITIONS
        transition_result = self._check_workflow_transition(
            user_input_lower, workflow_stage
        )
        if transition_result:
            return transition_result

        # Stage 3: Pattern-based classification
        intent, confidence = self._pattern_classify(user_input_lower)

        # Stage 4: Context evaluation
        context_score = self._evaluate_context(user_input, conversation_history, session_state)

        # Stage 5: Merge scores
        final_confidence = (confidence * 0.6) + (context_score * 0.4)

        # Stage 6: Determine if research needed
        requires_research = self._requires_deep_research(intent, final_confidence, session_state)

        # Stage 7: Recommend stage
        recommended_stage = self._recommend_stage(intent, workflow_stage)

        # Stage 8: Extract entities and needs
        entities = self._extract_entities(user_input)
        context_needs = self._determine_context_needs(intent, user_input)

        return IntentClassification(
            intent=intent,
            confidence=min(final_confidence, 0.95),
            requires_research=requires_research,
            suggested_behavior=self._get_behavior_mode(intent),
            extracted_entities=entities,
            context_needs=context_needs,
            is_continuation=False,
            recommended_stage=recommended_stage
        )

    def _check_continuation(self, text: str, active_topic: str,
                            workflow_stage: str, has_insights: bool) -> Optional[IntentClassification]:
        """Check if this is a continuation of active research."""

        # STRONG continuation signals
        continuation_patterns = [
            r'^(first|next|then|now|okay|ok)[,\s]+',
            r'^(let\'?s|let us)\s+(continue|proceed|move on|go deeper)',
            r'\b(go deeper|elaborate|tell me more|expand on)\b',
            r'^(what about|how about)\s+',
            r'\b(list|what are)\s+(the\s+)?(problems?|challenges?|issues?)\b',
            r'\b(list|what are)\s+(the\s+)?(solutions?|protocols?|projects?)\b',
            r'\b(who|which)\s+(is|are)\s+(solving|addressing|working on)\b',
            r'\b(what\s+if|how\s+would|what\s+about)\b',
        ]

        is_continuation = any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in continuation_patterns
        )

        # Check if topic-related
        topic_words = set(active_topic.lower().split())
        text_words = set(text.split())
        topic_overlap = len(topic_words & text_words) > 0

        # Check for pronouns referring to active topic
        pronoun_references = ['it', 'this', 'that', 'these', 'those', 'them']
        has_pronouns = any(p in text.split() for p in pronoun_references)

        if is_continuation or topic_overlap or (has_insights and has_pronouns):
            # Determine what kind of continuation

            # Research deepening
            if any(word in text for word in ['deep', 'deeper', 'elaborate', 'expand', 'more detail']):
                return IntentClassification(
                    intent=IntentType.RESEARCH_DEEPEN,
                    confidence=0.90,
                    requires_research=True,
                    suggested_behavior='deep_research_continuation',
                    extracted_entities=[],
                    context_needs=['previous_findings'],
                    is_continuation=True,
                    recommended_stage='investigation'
                )

            # Problem identification
            if any(word in text for word in ['problem', 'challenge', 'issue', 'risk', 'obstacle']):
                return IntentClassification(
                    intent=IntentType.RESEARCH_CONTINUATION,
                    confidence=0.92,
                    requires_research=True,
                    suggested_behavior='problem_identification',
                    extracted_entities=[],
                    context_needs=['active_topic_context'],
                    is_continuation=True,
                    recommended_stage='problem_analysis'
                )

            # Solution mapping
            if any(word in text for word in ['solution', 'protocol', 'project', 'who', 'solving', 'addressing']):
                return IntentClassification(
                    intent=IntentType.RESEARCH_CONTINUATION,
                    confidence=0.90,
                    requires_research=True,
                    suggested_behavior='ecosystem_mapping',
                    extracted_entities=[],
                    context_needs=['solution_landscape'],
                    is_continuation=True,
                    recommended_stage='solution_research'
                )

            # General continuation
            return IntentClassification(
                intent=IntentType.RESEARCH_CONTINUATION,
                confidence=0.85,
                requires_research=True,
                suggested_behavior='research_continuation',
                extracted_entities=[],
                context_needs=['conversation_history'],
                is_continuation=True,
                recommended_stage=workflow_stage
            )

        return None

    def _check_workflow_transition(self, text: str,
                                    current_stage: str) -> Optional[IntentClassification]:
        """Check if user is requesting workflow stage transition."""

        # Understanding → Investigation
        if current_stage == 'understanding' and \
           any(word in text for word in ['let\'s start', 'begin', 'dive in', 'get started', 'go']):
            return IntentClassification(
                intent=IntentType.WORKFLOW_TRANSITION,
                confidence=0.88,
                requires_research=True,
                suggested_behavior='transition_to_investigation',
                extracted_entities=[],
                context_needs=[],
                recommended_stage='investigation'
            )

        # Investigation → Analysis
        if current_stage == 'investigation' and \
           any(word in text for word in ['analyze', 'what does this mean', 'implications', 'patterns']):
            return IntentClassification(
                intent=IntentType.WORKFLOW_TRANSITION,
                confidence=0.85,
                requires_research=True,
                suggested_behavior='transition_to_analysis',
                extracted_entities=[],
                context_needs=[],
                recommended_stage='analysis'
            )

        return None

    def _pattern_classify(self, text: str) -> Tuple[IntentType, float]:
        """Pattern-based intent detection."""

        # GREETING patterns
        greeting_patterns = [
            r'^(hi|hello|hey|yo|hiya|greetings)[\s!.,]*$',
            r'^(good (morning|afternoon|evening))[ns!.,]*$',
            r'^(what\'?s up|howdy|sup)[\s!.,]*$',
        ]
        for pattern in greeting_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return IntentType.GREETING, 0.95

        # CASUAL_CONVERSATION patterns
        casual_patterns = [
            r'\b(how are you|how\'?s it going|what are you up to)\b',
            r'\b(thanks|thank you|appreciate it)\b',
            r'^(nice|cool|awesome|great)[\s!.,]*$',
        ]
        for pattern in casual_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.CASUAL_CONVERSATION, 0.85

        # COLLABORATION_INQUIRY patterns
        collab_patterns = [
            r'\b(work together|collaborate|partner|join forces)\b',
            r'\b(can we work|let\'?s work|help me with|assist with)\b',
            r'\b(looking for help|need help|seeking assistance)\b',
        ]
        for pattern in collab_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.COLLABORATION_INQUIRY, 0.88

        # RESEARCH_REQUEST patterns
        research_patterns = [
            r'\b(research|investigate|analyze|study|examine)\b.*\b(on|into|about)\b',
            r'\b(deep dive|deep analysis|comprehensive study|in-depth analysis)\b',
            r'\b(what is|how does|why does|how do|what are)\b.*\b(work|function|mechanism|ecosystem|problems|challenges|issues)\b',
            r'\b(validator economics|tokenomics|ecosystem analysis|market research|liquidity provision|defi)\b',
            r'\b(landscape|overview|assessment|evaluation) of\b',
            r'\b(compare|contrast|versus|vs)\b.*\b(with|and)\b',
            r'\b(problems?|challenges?|issues?)\b.*\b(with|in|on)\b',
        ]
        for pattern in research_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.RESEARCH_REQUEST, 0.92

        # OPPORTUNITY_SEARCH patterns
        opportunity_patterns = [
            r'\b(find|search|looking for)\b.*\b(grants?|jobs?|funding|opportunities?|bounties?)\b',
            r'\b(grant opportunities|job search|career opportunities|fellowship|stipend)\b',
        ]
        for pattern in opportunity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.OPPORTUNITY_SEARCH, 0.85

        # CONTENT_GENERATION patterns
        content_patterns = [
            r'\b(write|create|draft|generate)\b.*\b(thread|post|article|content|blog)\b',
            r'\b(twitter|x thread|linkedin post|blog post)\b',
        ]
        for pattern in content_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.CONTENT_GENERATION, 0.85

        # STRATEGIC_BRAINSTORMING patterns
        strategy_patterns = [
            r'\b(strategy|strategic|positioning|plan|approach)\b',
            r'\b(brainstorm|think through|figure out|game plan)\b',
            r'\b(should i|how should|what\'?s the best way to)\b',
        ]
        for pattern in strategy_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.STRATEGIC_BRAINSTORMING, 0.80

        # FOLLOW_UP_DISCUSSION patterns
        followup_patterns = [
            r'\b(follow up|following up|regarding|about that|you mentioned)\b',
            r'\b(earlier you said|previously|last time)\b',
        ]
        for pattern in followup_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.FOLLOW_UP_DISCUSSION, 0.80

        # Short inputs likely casual
        if len(text.split()) <= 3:
            return IntentType.CASUAL_CONVERSATION, 0.70

        return IntentType.AMBIGUOUS, 0.50

    def _evaluate_context(self, user_input: str,
                         history: List[Dict],
                         session_state: Dict) -> float:
        """Evaluate conversational context."""
        score = 0.5

        # Boost if active research session
        if session_state.get('active_topic'):
            score += 0.2

        # Boost if in research mode
        if session_state.get('conversation_mode') == 'research':
            score += 0.15

        # Check history for flow
        if history:
            last_message = history[-1] if history else None
            if last_message and last_message.get('role') == 'assistant':
                # If we asked a question, boost confidence
                if '?' in last_message.get('content', ''):
                    score += 0.1

        return min(score, 0.95)

    def _requires_deep_research(self, intent: IntentType,
                                confidence: float,
                                session_state: Dict) -> bool:
        """Determine if this requires deep research."""

        # Continue research if already in research mode
        if session_state.get('conversation_mode') == 'research':
            return True

        research_intents = {
            IntentType.RESEARCH_REQUEST,
            IntentType.RESEARCH_CONTINUATION,
            IntentType.RESEARCH_DEEPEN,
            IntentType.STRATEGIC_BRAINSTORMING,
        }

        if intent in research_intents and confidence >= 0.70:
            return True

        return False

    def _recommend_stage(self, intent: IntentType,
                        current_stage: str) -> Optional[str]:
        """Recommend next workflow stage."""

        stage_transitions = {
            IntentType.RESEARCH_REQUEST: 'understanding',
            IntentType.RESEARCH_CONTINUATION: current_stage,
            IntentType.RESEARCH_DEEPEN: 'investigation',
            IntentType.WORKFLOW_TRANSITION: 'investigation',
            IntentType.STRATEGIC_BRAINSTORMING: 'synthesis',
        }

        return stage_transitions.get(intent)

    def _get_behavior_mode(self, intent: IntentType) -> str:
        """Get suggested behavior mode."""
        mode_map = {
            IntentType.GREETING: "conversational_natural",
            IntentType.CASUAL_CONVERSATION: "conversational_collaborative",
            IntentType.COLLABORATION_INQUIRY: "collaborative_exploratory",
            IntentType.RESEARCH_REQUEST: "deep_research",
            IntentType.RESEARCH_CONTINUATION: "research_continuation",
            IntentType.RESEARCH_DEEPEN: "deep_research",
            IntentType.OPPORTUNITY_SEARCH: "opportunity_discovery",
            IntentType.CONTENT_GENERATION: "content_creation",
            IntentType.STRATEGIC_BRAINSTORMING: "strategic_planning",
            IntentType.EXECUTION_TASK: "execution_assist",
            IntentType.CLARIFICATION_REQUEST: "clarification",
            IntentType.FOLLOW_UP_DISCUSSION: "contextual_followup",
            IntentType.WORKFLOW_TRANSITION: "workflow_transition",
            IntentType.AMBIGUOUS: "clarification_needed",
        }
        return mode_map.get(intent, "conversational")

    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities."""
        entities = []

        # Crypto/protocol names
        crypto_pattern = r'\b(Bitcoin|Ethereum|Solana|Cardano|Avalanche|Polygon|Cosmos|Polkadot|\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\b'
        matches = re.findall(crypto_pattern, text)
        entities.extend(matches)

        # Research topics
        topic_pattern = r'\b(economics|tokenomics|validation|staking|DeFi|governance|consensus|liquidity|provision)\b'
        matches = re.findall(topic_pattern, text, re.IGNORECASE)
        entities.extend(matches)

        return list(set(entities))

    def _determine_context_needs(self, intent: IntentType, text: str) -> List[str]:
        """Determine what context is needed."""
        needs = []

        if intent in [IntentType.RESEARCH_CONTINUATION, IntentType.RESEARCH_DEEPEN]:
            needs.append("conversation_history")
            needs.append("previous_findings")

        if intent == IntentType.STRATEGIC_BRAINSTORMING:
            needs.append("user_background")

        if intent == IntentType.FOLLOW_UP_DISCUSSION:
            needs.append("conversation_history")

        return needs
