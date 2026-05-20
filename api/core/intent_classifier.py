"""GIDBoy Intent Classification System.

Distinguishes between different interaction types BEFORE any orchestration.
Never forces research mode on casual conversation.
"""
from enum import Enum, auto
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import re


class IntentType(Enum):
    """Classification of user intent."""
    GREETING = "greeting"
    CASUAL_CONVERSATION = "casual_conversation"
    COLLABORATION_INQUIRY = "collaboration_inquiry"
    RESEARCH_REQUEST = "research_request"
    OPPORTUNITY_SEARCH = "opportunity_search"
    CONTENT_GENERATION = "content_generation"
    STRATEGIC_BRAINSTORMING = "strategic_brainstorming"
    EXECUTION_TASK = "execution_task"
    CLARIFICATION_REQUEST = "clarification_request"
    FOLLOW_UP_DISCUSSION = "follow_up_discussion"
    AMBIGUOUS = "ambiguous"


@dataclass
class IntentClassification:
    """Result of intent classification."""
    intent: IntentType
    confidence: float  # 0.0 - 1.0
    requires_research: bool
    suggested_behavior: str
    extracted_entities: List[str]
    context_needs: List[str]


class IntentClassifier:
    """
    Classifies user input intent before any orchestration.

    NEVER forces research on casual input.
    NEVER hallucinates contexts.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def classify(self, user_input: str, conversation_history: List[Dict] = None) -> IntentClassification:
        """
        Classify user intent with confidence scoring.

        Returns classification BEFORE any workflow activation.
        """
        user_input_lower = user_input.lower().strip()

        # Stage 1: Pattern-based classification (fast, deterministic)
        intent, confidence = self._pattern_classify(user_input_lower)

        # Stage 2: Context evaluation
        context_score = self._evaluate_context(user_input, conversation_history)

        # Stage 3: Merge scores
        final_confidence = (confidence * 0.6) + (context_score * 0.4)

        # Stage 4: Determine if research needed
        requires_research = self._requires_deep_research(intent, final_confidence)

        # Stage 5: Extract entities and needs
        entities = self._extract_entities(user_input)
        context_needs = self._determine_context_needs(intent, user_input)

        return IntentClassification(
            intent=intent,
            confidence=min(final_confidence, 0.95),  # Cap at 0.95 to avoid false certainty
            requires_research=requires_research,
            suggested_behavior=self._get_behavior_mode(intent),
            extracted_entities=entities,
            context_needs=context_needs
        )

    def _pattern_classify(self, text: str) -> Tuple[IntentType, float]:
        """Pattern-based intent detection."""

        # GREETING patterns
        greeting_patterns = [
            r'^(hi|hello|hey|yo|hiya|greetings)[\s!.,]*$',
            r'^(good (morning|afternoon|evening))[\s!.,]*$',
            r'^(what\'?s up|howdy|sup)[\s!.,]*$',
        ]
        for pattern in greeting_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return IntentType.GREETING, 0.95

        # CASUAL_CONVERSATION patterns
        casual_patterns = [
            r'\b(how are you|how\'?s it going|what are you up to)\b',
            r'\b(can we work together|let\'?s collaborate|want to work)\b',
            r'\b(thanks|thank you|appreciate it)\b',
            r'^(nice|cool|awesome|great)[\s!.,]*$',
            r'\b(tell me about yourself|what do you do)\b',
        ]
        for pattern in casual_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.CASUAL_CONVERSATION, 0.85

        # COLLABORATION_INQUIRY patterns
        collab_patterns = [
            r'\b(work together|collaborate|partner|join forces)\b',
            r'\b(can you help me|help with|assist with)\b',
            r'\b(looking for|need help|seeking assistance)\b',
        ]
        for pattern in collab_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.COLLABORATION_INQUIRY, 0.80

        # RESEARCH_REQUEST patterns - ONLY trigger if clear research intent
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
                return IntentType.RESEARCH_REQUEST, 0.90

        # OPPORTUNITY_SEARCH patterns
        opportunity_patterns = [
            r'\b(find|search|looking for)\b.*\b(grants?|jobs?|funding|opportunities?|bounties?)\b',
            r'\b(grant opportunities|job search|career opportunities)\b',
            r'\b(fellowship|stipend|position|role)\b',
        ]
        for pattern in opportunity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.OPPORTUNITY_SEARCH, 0.85

        # CONTENT_GENERATION patterns
        content_patterns = [
            r'\b(write|create|draft|generate)\b.*\b(thread|post|article|content|blog|newsletter)\b',
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

        # EXECUTION_TASK patterns
        execution_patterns = [
            r'\b(draft|write|send|apply|submit)\b.*\b(email|application|proposal|message)\b',
            r'\b(outreach|contact|reach out to)\b',
            r'\b(help me (draft|write|create))\b',
        ]
        for pattern in execution_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.EXECUTION_TASK, 0.85

        # CLARIFICATION_REQUEST patterns
        clarification_patterns = [
            r'\b(what do you mean|can you explain|clarify|i don\'?t understand)\b',
            r'\b(confused about|unclear on|question about)\b',
        ]
        for pattern in clarification_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.CLARIFICATION_REQUEST, 0.80

        # FOLLOW_UP_DISCUSSION patterns
        followup_patterns = [
            r'\b(follow up|following up|regarding|about that|you mentioned)\b',
            r'\b(earlier you said|previously|last time)\b',
        ]
        for pattern in followup_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return IntentType.FOLLOW_UP_DISCUSSION, 0.75

        # Short inputs are likely casual unless specific keywords
        if len(text.split()) <= 3:
            return IntentType.CASUAL_CONVERSATION, 0.70

        # Default to ambiguous if unclear
        return IntentType.AMBIGUOUS, 0.50

    def _evaluate_context(self, user_input: str, history: List[Dict] = None) -> float:
        """Evaluate conversational context for intent confidence."""
        if not history:
            return 0.5  # No context

        # Check if this is a follow-up
        last_exchange = history[-1] if history else None
        if last_exchange:
            # If user is responding to our question, increase confidence
            if '?' in last_exchange.get('response', ''):
                return 0.8

        return 0.6

    def _requires_deep_research(self, intent: IntentType, confidence: float) -> bool:
        """Determine if this intent requires deep research workflow."""
        # ONLY research-heavy intents should trigger research
        research_intents = {
            IntentType.RESEARCH_REQUEST,
            IntentType.STRATEGIC_BRAINSTORMING,
        }

        # High confidence + research intent
        if intent in research_intents and confidence >= 0.75:
            return True

        # Opportunity search might need light research
        if intent == IntentType.OPPORTUNITY_SEARCH and confidence >= 0.85:
            return True

        return False

    def _get_behavior_mode(self, intent: IntentType) -> str:
        """Get suggested behavior mode for intent."""
        mode_map = {
            IntentType.GREETING: "conversational_natural",
            IntentType.CASUAL_CONVERSATION: "conversational_collaborative",
            IntentType.COLLABORATION_INQUIRY: "collaborative_exploratory",
            IntentType.RESEARCH_REQUEST: "deep_research",
            IntentType.OPPORTUNITY_SEARCH: "opportunity_discovery",
            IntentType.CONTENT_GENERATION: "content_creation",
            IntentType.STRATEGIC_BRAINSTORMING: "strategic_planning",
            IntentType.EXECUTION_TASK: "execution_assist",
            IntentType.CLARIFICATION_REQUEST: "clarification",
            IntentType.FOLLOW_UP_DISCUSSION: "contextual_followup",
            IntentType.AMBIGUOUS: "clarification_needed",
        }
        return mode_map.get(intent, "conversational")

    def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities from input."""
        entities = []

        # Extract crypto/protocol names
        crypto_pattern = r'\b(Bitcoin|Ethereum|Solana|Cardano|Avalanche|Polygon|Cosmos|Polkadot|\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b)\b'
        matches = re.findall(crypto_pattern, text)
        entities.extend(matches)

        # Extract research topics
        topic_pattern = r'\b(economics|tokenomics|validation|staking|DeFi|governance|consensus)\b'
        matches = re.findall(topic_pattern, text, re.IGNORECASE)
        entities.extend(matches)

        return list(set(entities))

    def _determine_context_needs(self, intent: IntentType, text: str) -> List[str]:
        """Determine what context is needed."""
        needs = []

        if intent == IntentType.FOLLOW_UP_DISCUSSION:
            needs.append("conversation_history")

        if intent == IntentType.STRATEGIC_BRAINSTORMING:
            needs.append("user_background")
            needs.append("goals")

        if IntentType.RESEARCH_REQUEST:
            # Check if specific enough
            if len(text.split()) < 5:
                needs.append("clarification")

        return needs

    def should_clarify(self, classification: IntentClassification) -> bool:
        """Determine if we should ask for clarification."""
        if classification.intent == IntentType.AMBIGUOUS:
            return True
        if classification.confidence < 0.60:
            return True
        if IntentType.RESEARCH_REQUEST and len(classification.context_needs) > 0:
            return True
        return False

    def get_clarification_prompt(self, classification: IntentClassification, original_input: str) -> str:
        """Generate clarification request based on ambiguous input."""
        if classification.intent == IntentType.AMBIGUOUS:
            return f"I'd like to help with '{original_input}'. Could you clarify what you're looking for? For example:\n\n• Research on a specific topic?\n• Help with a collaboration?\n• Just saying hi?\n• Looking for opportunities?"

        if classification.intent == IntentType.RESEARCH_REQUEST and "clarification" in classification.context_needs:
            return f"I can research that for you. To give you the most useful analysis, could you be more specific about:\n\n• What aspect interests you most?\n• What depth are you looking for (overview vs deep dive)?\n• Any specific questions you want answered?"

        return "Could you tell me more about what you're looking for?"


# Simple conversational response generator
class ConversationalResponder:
    """Generates natural conversational responses (NO fake research)."""

    def generate_greeting(self) -> str:
        """Natural greeting response."""
        import random
        greetings = [
            "Hey there! Ready to dig into some research?",
            "Hi! What are we exploring today?",
            "Hello! What ecosystem or topic should we investigate?",
            "Hey! I'm here to help with deep research and strategic thinking. What's on your mind?",
        ]
        return random.choice(greetings)

    def generate_collaboration_response(self, user_input: str) -> str:
        """Collaborative inquiry response."""
        return """I'd love to collaborate! Here's how we can work together:

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

    def generate_casual_response(self, user_input: str) -> str:
        """Natural casual conversation."""
        import random

        if "how are you" in user_input.lower():
            responses = [
                "Doing well, thanks! Always ready to dive into some ecosystem research. What about you?",
                "I'm good! Excited to dig into whatever you're working on. What's on your mind?",
            ]
            return random.choice(responses)

        if "thank" in user_input.lower():
            return "You're welcome! Let me know if there's anything else I can help research or analyze."

        if "can we work" in user_input.lower() or "collaborate" in user_input.lower():
            return self.generate_collaboration_response(user_input)

        # Default casual
        casual = [
            "I'm here when you're ready to dive into something. What are you thinking about?",
            "Ready when you are! What ecosystem or topic should we explore?",
            "What's on your research radar today?",
        ]
        return random.choice(casual)

    def generate_ambiguous_response(self, user_input: str) -> str:
        """Ask for clarification naturally."""
        return f"I'd like to help with that! Could you clarify a bit? Are you looking for:\n\n• Research on a specific topic?\n• Help finding opportunities?\n• Strategic brainstorming?\n• Or just chatting?\n\nLet me know what you're after and I'll jump in."


# Main router that uses intent classification
class IntentRouter:
    """Routes user input based on classified intent."""

    def __init__(self, llm_client=None):
        self.classifier = IntentClassifier(llm_client)
        self.responder = ConversationalResponder()

    def route(self, user_input: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Route user input based on intent.

        Returns routing decision and appropriate response strategy.
        """
        # Classify intent
        classification = self.classifier.classify(user_input, conversation_history)

        # Determine routing
        result = {
            "intent": classification.intent.value,
            "confidence": classification.confidence,
            "requires_research": classification.requires_research,
            "behavior_mode": classification.suggested_behavior,
            "entities": classification.extracted_entities,
        }

        # Handle based on intent
        if classification.intent == IntentType.GREETING:
            result["response"] = self.responder.generate_greeting()
            result["workflow"] = "conversational"

        elif classification.intent == IntentType.CASUAL_CONVERSATION:
            result["response"] = self.responder.generate_casual_response(user_input)
            result["workflow"] = "conversational"

        elif classification.intent == IntentType.COLLABORATION_INQUIRY:
            result["response"] = self.responder.generate_collaboration_response(user_input)
            result["workflow"] = "collaborative"

        elif classification.intent == IntentType.AMBIGUOUS:
            result["response"] = self.responder.generate_ambiguous_response(user_input)
            result["workflow"] = "clarification"
            result["should_clarify"] = True

        elif classification.requires_research:
            # Only now do we activate research workflow
            result["workflow"] = "deep_research"
            result["response"] = None  # Will be generated by research engine

        else:
            # Default conversational
            result["response"] = self.responder.generate_casual_response(user_input)
            result["workflow"] = "conversational"

        return result
