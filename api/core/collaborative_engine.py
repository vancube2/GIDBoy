"""GIDBoy Collaborative Intelligence Engine.

This is NOT a multi-agent pipeline.
This is a continuous reasoning process that deepens understanding.

The user should feel like they're working with a research strategist,
not using ChatGPT with plugins.
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .intelligence_context import IntelligenceContext, ReasoningStep, CollaborativeIntelligenceEngine


class CollaborativeReasoningEngine:
    """
    Orchestrates deep collaborative reasoning.

    Key principle: The response evolves like a real analyst would think,
    not like modular AI components stacked together.
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.context: Optional[IntelligenceContext] = None

    def collaborate(self, query: str, memory_context: str = "") -> Dict[str, Any]:
        """
        Execute full collaborative intelligence process.

        Returns ONE evolving narrative, not isolated agent outputs.
        """
        # Initialize shared context
        self.context = IntelligenceContext(query=query)

        # STAGE 1: Collaborative Understanding
        self._stage_understanding(query, memory_context)

        # STAGE 2: Deep Investigation
        self._stage_investigation()

        # STAGE 3: Pattern Recognition & Analysis
        self._stage_analysis()

        # STAGE 4: Hypothesis Generation (multiple, competing)
        self._stage_hypotheses()

        # STAGE 5: Strategic Interpretation
        self._stage_strategic_interpretation()

        # STAGE 6: Opportunity Discovery (emerges from strategy)
        self._stage_opportunity_discovery()

        # STAGE 7: Action Pathways
        self._stage_action_pathways()

        # STAGE 8: Content/Positioning (emerges from insight)
        self._stage_positioning()

        # Return unified collaborative response
        return self._synthesize_collaborative_response()

    def _call_reasoning_llm(self, prompt: str, system_context: str = "") -> str:
        """Call LLM with reasoning-focused parameters."""
        if not self.llm_client:
            return self._generate_fallback_reasoning(prompt)

        return self.llm_client(
            prompt=prompt,
            system_prompt=system_context,
            temperature=0.4,  # Allow some creativity in reasoning
            max_tokens=4000   # Allow depth
        )

    def _stage_understanding(self, query: str, memory_context: str):
        """Stage 1: What are we actually trying to understand?"""

        prompt = f"""You are collaborating with a user on deep research.

QUERY: {query}

PREVIOUS RELATED WORK: {memory_context}

Your task: Help understand what we're actually investigating.

Think through:
1. What is the core question beneath the surface question?
2. Why does this matter? Who is affected?
3. What assumptions might we be bringing?
4. What do we NOT know yet that we should?

Respond in this format:

PROBLEM UNDERSTANDING: [2-3 sentences on what we're really investigating]

WHY IT MATTERS: [The stakes, who cares, ecosystem implications]

KEY ASSUMPTIONS: [What are we assuming that we should question?]

WHAT WE DON'T KNOW: [Critical information gaps]
"""

        response = self._call_reasoning_llm(
            prompt,
            "You are a research strategist. Think deeply, question assumptions, identify gaps."
        )

        # Parse and add to context
        parsed = self._parse_stage_response(response)

        self.context.problem_understanding = parsed.get("PROBLEM UNDERSTANDING", "")
        self.context.why_it_matters = parsed.get("WHY IT MATTERS", "")
        self.context.key_assumptions = self._bullet_list(parsed.get("KEY ASSUMPTIONS", ""))
        self.context.known_unknowns = self._bullet_list(parsed.get("WHAT WE DON'T KNOW", ""))

        self.context.add_reasoning_step(
            stage="understanding",
            thought=self.context.problem_understanding,
            uncertainties=self.context.known_unknowns,
            confidence=0.6  # Low confidence at this stage - we're just starting
        )

    def _stage_investigation(self):
        """Stage 2: Deep investigation and evidence gathering."""

        prompt = f"""Now let's investigate. Based on our understanding:

{self.context.problem_understanding}

What ecosystems, technologies, and dynamics should we map?

Investigate:
1. What systems are involved?
2. Who are the key actors and what are their incentives?
3. What market dynamics are at play?
4. What historical context matters?
5. What evidence/data points are most important?

Map this deeply. Think like an ecosystem analyst.

Respond:

ECOSYSTEM MAP: [Systems, actors, relationships]

KEY ACTORS: [Major players and their motivations]

MARKET DYNAMICS: [Forces at play]

HISTORICAL CONTEXT: [How did we get here?]

KEY EVIDENCE: [Critical data points and findings]
"""

        response = self._call_reasoning_llm(prompt)
        parsed = self._parse_stage_response(response)

        self.context.ecosystem_map = {"description": parsed.get("ECOSYSTEM MAP", "")}
        self.context.market_dynamics = parsed.get("MARKET DYNAMICS", "")
        self.context.historical_context = parsed.get("HISTORICAL CONTEXT", "")

        # Extract evidence
        evidence_text = parsed.get("KEY EVIDENCE", "")
        self.context.key_findings = self._extract_findings(evidence_text)

        self.context.add_reasoning_step(
            stage="investigation",
            thought=f"Investigated ecosystem: {parsed.get('ECOSYSTEM MAP', '')[:200]}...",
            evidence=self.context.key_findings,
            confidence=0.7
        )

    def _stage_analysis(self):
        """Stage 3: Pattern recognition and analysis."""

        prompt = f"""Now let's analyze what we've found.

Evidence gathered:
{chr(10).join(['- ' + f for f in self.context.key_findings[:5]])}

Questions to explore:
1. What patterns emerge from this evidence?
2. What contradictions or tensions exist?
3. What incentives are misaligned?
4. What would an outsider miss?
5. What is counterintuitive here?

Think critically. Look for what's hidden.

Respond:

PATTERNS IDENTIFIED: [Emerging patterns]

CONTRADICTIONS: [Tensions in the data]

HIDDEN DYNAMICS: [What's beneath the surface]
"""

        response = self._call_reasoning_llm(prompt)
        parsed = self._parse_stage_response(response)

        patterns = self._bullet_list(parsed.get("PATTERNS IDENTIFIED", ""))
        contradictions = parsed.get("CONTRADICTIONS", "")

        self.context.add_reasoning_step(
            stage="analysis",
            thought=f"Analysis reveals patterns: {patterns[0] if patterns else 'Investigating...'}",
            evidence=patterns,
            contradictions=self._bullet_list(contradictions),
            confidence=0.75
        )

    def _stage_hypotheses(self):
        """Stage 4: Generate MULTIPLE competing hypotheses."""

        prompt = f"""Based on our investigation and analysis:

Findings: {self.context.key_findings[:3]}
Patterns: {[s.thought for s in self.context.reasoning_trail if s.stage == 'analysis']}

Generate MULTIPLE hypotheses. Do NOT converge on one yet.

Hypothesis A (Primary): [Best supported by evidence]
Hypothesis B (Alternative): [Different interpretation]
Hypothesis C (Edge case): [What if we're wrong?]

For each:
- What evidence supports it?
- What evidence contradicts it?
- What would prove/disprove it?
- Confidence level?

Embrace uncertainty. Multiple hypotheses can coexist.
"""

        response = self._call_reasoning_llm(prompt)

        # Parse hypotheses
        import re
        hypothesis_pattern = r'Hypothesis [ABC][^:]*:([^\n]+(?:\n(?!(?:Hypothesis|Respond|For each))[^\n]+)*)'
        matches = re.findall(hypothesis_pattern, response, re.IGNORECASE)

        for i, match in enumerate(matches[:3]):
            self.context.add_hypothesis(
                hypothesis=match.strip()[:200],
                evidence=["Evidence gathered"],
                confidence=0.6 if i == 0 else 0.4  # Primary gets slightly higher
            )

        self.context.add_reasoning_step(
            stage="hypothesis_generation",
            thought=f"Generated {len(matches)} competing hypotheses. Not converging prematurely.",
            uncertainties=["Which hypothesis is correct?", "What would falsify each?"],
            confidence=0.5  # Low confidence - still exploring
        )

    def _stage_strategic_interpretation(self):
        """Stage 5: What does this mean strategically?"""

        prompt = f"""Now: Strategic interpretation.

Given our investigation and hypotheses, what does this MEAN?

Consider:
1. First-order effects (immediate impact)
2. Second-order effects (ripple effects)
3. Third-order effects (systemic shifts)
4. Who benefits? Who is threatened?
5. What shifts in power or value?

This should emerge from the research, not be generic.

Respond:

STRATEGIC IMPLICATIONS: [What this means]

FIRST-ORDER EFFECTS: [Immediate changes]

SECOND-ORDER EFFECTS: [Ripple impacts]

WHO BENEFITS: [Actors positioned well]

ECOSYSTEM SHIFTS: [How the landscape changes]
"""

        response = self._call_reasoning_llm(prompt)
        parsed = self._parse_stage_response(response)

        self.context.strategic_implications = parsed.get("STRATEGIC IMPLICATIONS", "")
        self.context.first_order_effects = self._bullet_list(parsed.get("FIRST-ORDER EFFECTS", ""))
        self.context.second_order_effects = self._bullet_list(parsed.get("SECOND-ORDER EFFECTS", ""))
        self.context.who_would_value_this = self._bullet_list(parsed.get("WHO BENEFITS", ""))

        self.context.add_reasoning_step(
            stage="strategic_interpretation",
            thought=self.context.strategic_implications,
            evidence=self.context.first_order_effects,
            confidence=0.65
        )

    def _stage_opportunity_discovery(self):
        """Stage 6: Opportunities EMERGE from strategic understanding."""

        prompt = f"""Opportunity discovery (NOT generic generation).

Based on strategic implications:
{self.context.strategic_implications}

And who benefits:
{chr(10).join(self.context.who_would_value_this)}

Ask:
1. What organizations/people would VALUE this understanding?
2. Why would they care specifically?
3. What could they DO with this intelligence?
4. How can the user POSITION to capture this value?

Opportunities should EMERGE naturally, not be listed generically.

Respond:

EMERGED OPPORTUNITIES: [Specific opportunities tied to findings]

FOR EACH: Explain WHY this organization cares and HOW they could use this.

POSITIONING ANGLES: [How user should position]
"""

        response = self._call_reasoning_llm(prompt)

        # Extract opportunities (they should be specific and tied to findings)
        opportunities = self._extract_opportunities(response)
        for opp in opportunities:
            self.context.discover_opportunity(
                opportunity=opp.get("opportunity", ""),
                source=opp.get("source", "strategic analysis"),
                relevance=opp.get("relevance", ""),
                action=opp.get("action", "")
            )

        self.context.positioning_angles = self._extract_positioning(response)

        self.context.add_reasoning_step(
            stage="opportunity_discovery",
            thought=f"Discovered {len(opportunities)} opportunities that emerge naturally from strategic analysis",
            evidence=[o.get("opportunity", "") for o in opportunities],
            confidence=0.7
        )

    def _stage_action_pathways(self):
        """Stage 7: Action pathways emerge from opportunities."""

        prompt = f"""Action pathway development.

Given discovered opportunities:
{chr(10).join([o.get('opportunity', '') for o in self.context.discovered_opportunities[:3]])}

Develop concrete action pathways:

IMMEDIATE (This week):
- What specific first step?
- Who to reach out to?
- What to prepare?

SHORT-TERM (This month):
- What moves to make?
- How to build momentum?
- What to track?

MEDIUM-TERM (This quarter):
- Strategic positioning
- Relationship building
- Value capture

Each action should connect to discovered opportunities.
"""

        response = self._call_reasoning_llm(prompt)
        parsed = self._parse_stage_response(response)

        self.context.immediate_moves = self._bullet_list(parsed.get("IMMEDIATE", ""))
        self.context.short_term_strategy = parsed.get("SHORT-TERM", "")
        self.context.medium_term_strategy = parsed.get("MEDIUM-TERM", "")

        self.context.add_reasoning_step(
            stage="action_development",
            thought="Action pathways emerge from opportunity discovery",
            confidence=0.75
        )

    def _stage_positioning(self):
        """Stage 8: Content/positioning emerges from insight."""

        prompt = f"""Content and positioning (emerges from insight).

Core insights discovered:
{chr(10).join(self.context.key_findings[:3])}

Strategic angle:
{self.context.strategic_implications[:200]}

Develop:

CORE INSIGHTS TO SHARE: [What original thinking to publish?]

NARRATIVE THREADS: [How to tell this story?]

POSITIONING: [How to establish authority]

This should feel like original research, not recycled content.
"""

        response = self._call_reasoning_llm(prompt)
        parsed = self._parse_stage_response(response)

        self.context.core_insights = self._bullet_list(parsed.get("CORE INSIGHTS TO SHARE", ""))
        self.context.narrative_threads = self._bullet_list(parsed.get("NARRATIVE THREADS", ""))

        self.context.add_reasoning_step(
            stage="positioning",
            thought="Positioning emerges from original insight",
            confidence=0.8
        )

    def _synthesize_collaborative_response(self) -> Dict[str, Any]:
        """
        Synthesize into ONE collaborative response.

        NOT modular outputs.
        ONE evolving intelligence narrative.
        """
        ctx = self.context

        # Build reasoning narrative
        reasoning_narrative = []
        for step in ctx.reasoning_trail:
            reasoning_narrative.append({
                "stage": step.stage,
                "thought": step.thought,
                "confidence": step.confidence,
                "uncertainties": step.uncertainties
            })

        return {
            "collaborative_intelligence_session": {
                "query": ctx.query,
                "status": "complete",

                "investigation_process": {
                    "what_we_sought_to_understand": ctx.problem_understanding,
                    "why_it_matters": ctx.why_it_matters,
                    "assumptions_we_questioned": ctx.key_assumptions,
                    "ecosystem_mapped": ctx.ecosystem_map,
                    "evidence_gathered": ctx.key_findings,
                },

                "reasoning_process": {
                    "hypotheses_considered": [
                        {
                            "hypothesis": h["hypothesis"],
                            "confidence": h["confidence"]
                        }
                        for h in ctx.hypotheses
                    ],
                    "what_remains_uncertain": ctx.known_unknowns,
                    "contradictions_noted": ctx.contradictions,
                },

                "strategic_interpretation": {
                    "what_this_means": ctx.strategic_implications,
                    "first_order_effects": ctx.first_order_effects,
                    "second_order_effects": ctx.second_order_effects,
                    "who_benefits_from_this_understanding": ctx.who_would_value_this,
                },

                "discovered_opportunities": [
                    {
                        "opportunity": o.get("opportunity"),
                        "source": o.get("source"),
                        "relevance": o.get("relevance"),
                        "action": o.get("action")
                    }
                    for o in ctx.discovered_opportunities
                ],

                "action_pathways": {
                    "immediate_moves": ctx.immediate_moves,
                    "short_term_strategy": ctx.short_term_strategy,
                    "medium_term_strategy": ctx.medium_term_strategy,
                },

                "positioning_from_insight": {
                    "core_insights_to_share": ctx.core_insights,
                    "narrative_threads": ctx.narrative_threads,
                    "positioning_angles": ctx.positioning_angles,
                },

                "reasoning_trail": reasoning_narrative,
                "current_stage": ctx.current_stage,
            }
        }

    # Helper methods
    def _parse_stage_response(self, response: str) -> Dict[str, str]:
        """Parse stage response into key-value pairs."""
        import re
        result = {}
        current_key = None
        current_value = []

        for line in response.split('\n'):
            # Look for headers like "KEY: value" or "**KEY**: value"
            match = re.match(r'(?:\*\*)?([A-Z][A-Z\s]+)(?:\*\*)?:\s*(.+)?', line)
            if match:
                if current_key:
                    result[current_key] = '\n'.join(current_value).strip()
                current_key = match.group(1).strip()
                current_value = [match.group(2)] if match.group(2) else []
            elif current_key and line.strip():
                current_value.append(line)

        if current_key:
            result[current_key] = '\n'.join(current_value).strip()

        return result

    def _bullet_list(self, text: str) -> List[str]:
        """Extract bullet points from text."""
        lines = text.split('\n')
        bullets = []
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                bullets.append(line[1:].strip())
            elif line and not line.endswith(':'):
                bullets.append(line)
        return bullets if bullets else [text] if text else []

    def _extract_findings(self, text: str) -> List[str]:
        """Extract findings from evidence text."""
        return self._bullet_list(text)

    def _extract_opportunities(self, text: str) -> List[Dict[str, str]]:
        """Extract specific opportunities from text."""
        import re
        opportunities = []

        # Look for patterns like "- Opportunity: ..." or numbered lists
        opp_pattern = r'(?:^|\n)(?:\d+\.|-)\s*([^:]+):?([^\n]+(?:\n(?!(?:\d+\.|-))[^\n]+)*)'
        matches = re.findall(opp_pattern, text, re.MULTILINE)

        for match in matches:
            opportunities.append({
                "opportunity": match[0].strip(),
                "relevance": match[1].strip() if len(match) > 1 else "",
                "source": "strategic interpretation",
                "action": "Investigate further"
            })

        return opportunities if opportunities else [{
            "opportunity": "Research positioning in this ecosystem",
            "source": "strategic analysis",
            "relevance": "User has developed deep understanding",
            "action": "Publish findings and engage with ecosystem"
        }]

    def _extract_positioning(self, text: str) -> List[str]:
        """Extract positioning angles from text."""
        return self._bullet_list(text)

    def _generate_fallback_reasoning(self, prompt: str) -> str:
        """Generate fallback reasoning when LLM unavailable."""
        return """PROBLEM UNDERSTANDING: Complex ecosystem dynamics requiring deep investigation

WHY IT MATTERS: Strategic implications for positioning and opportunity

KEY ASSUMPTIONS:
- Surface narrative may not reflect reality
- Multiple interpretations possible
- Incentives drive behavior

WHAT WE DON'T KNOW:
- Full ecosystem map
- All actor incentives
- Future developments
"""
