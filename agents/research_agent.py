"""GIDBoy Research Agent - Deep investigation and analysis."""
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentState


class ResearchAgent(BaseAgent):
    """
    Research Agent performs deep investigation following the 7-step process:
    1. Problem Understanding
    2. Context Mapping
    3. Evidence Gathering
    4. Hypothesis Generation
    5. Contradiction Analysis
    6. Solution Exploration
    7. Strategic Implications
    """

    def __init__(self, llm_client=None):
        super().__init__("Research", llm_client)
        self.research_prompt = """You are the GIDBoy Research Engine.

TASK: {query}

MEMORY CONTEXT:
{memory}

Follow this research process rigorously:

## STEP 1: PROBLEM UNDERSTANDING
Define the actual problem:
- What is the core question?
- Why does it matter?
- Who is affected?
- What assumptions exist?

## STEP 2: CONTEXT MAPPING
Map the ecosystem:
- What systems are involved?
- What technologies matter?
- What market dynamics?
- What historical context?

## STEP 3: EVIDENCE GATHERING
Investigate and gather evidence:
- What data is available?
- What are the key facts?
- What are the trends?
- What do experts say?

## STEP 4: HYPOTHESIS GENERATION
Generate multiple hypotheses:
- Hypothesis A: [explanation and evidence]
- Hypothesis B: [alternative explanation]
- Hypothesis C: [edge case or contrarian view]
Do NOT prematurely collapse into one narrative.

## STEP 5: CONTRADICTION ANALYSIS
Identify contradictions and tensions:
- What evidence contradicts?
- What incentives are misaligned?
- What assumptions may be wrong?

## STEP 6: SOLUTION EXPLORATION
Propose solutions and analyze:
- Solution 1: [description + tradeoffs]
- Solution 2: [description + tradeoffs]
- Solution 3: [description + tradeoffs]

## STEP 7: STRATEGIC IMPLICATIONS
What does this mean strategically?
- First-order effects
- Second-order effects
- Ecosystem implications
- Who benefits?

## OUTPUT FORMAT
Return your findings in this structure:

**EXECUTIVE SUMMARY**
[2-3 sentences on key findings]

**PROBLEM ANALYSIS**
[Deep analysis of the problem]

**ECOSYSTEM MAPPING**
[System context and players]

**KEY FINDINGS**
- Finding 1: [with evidence]
- Finding 2: [with evidence]
- Finding 3: [with evidence]

**HYPOTHESES**
- Primary: [best supported]
- Alternative: [other valid interpretation]
- Edge Case: [what if we're wrong]

**CONTRADICTIONS IDENTIFIED**
[Tensions and conflicts in the data]

**SOLUTIONS**
1. [Solution name]
   - Approach: [how it works]
   - Tradeoffs: [pros/cons]
   - Timeline: [implementation]

**STRATEGIC IMPLICATIONS**
[What this means for the ecosystem]

**UNCERTAINTIES**
[What remains unknown]

**NEXT RESEARCH DIRECTIONS**
[What to investigate next]"""

    def process(self, state: AgentState) -> AgentState:
        """Execute deep research workflow."""
        self.log_reasoning("start", f"Starting research on: {state.query}")

        # Format memory context
        memory_text = self._format_memory(state.memory)

        # Build research prompt
        prompt = self.research_prompt.format(
            query=state.query,
            memory=memory_text
        )

        # Call LLM
        if self.llm_client:
            response = self.llm_client(
                prompt=prompt,
                temperature=0.3,
                max_tokens=4000
            )
        else:
            response = self._generate_fallback_research(state.query)

        # Parse and structure output
        research_output = self._structure_research_output(response)

        # Update state
        state.output["research"] = research_output
        state.output["raw_response"] = response
        state.status = "completed"

        self.log_reasoning("complete", "Research completed with structured analysis")

        return state

    def _format_memory(self, memory: List[Dict[str, Any]]) -> str:
        """Format memory for context."""
        if not memory:
            return "No relevant memory found."

        memory_texts = []
        for item in memory[:3]:  # Top 3 relevant memories
            memory_texts.append(
                f"- Previous: {item.get('query', 'N/A')}\n  "
                f"Finding: {str(item.get('response', 'N/A'))[:200]}..."
            )

        return "\n".join(memory_texts)

    def _structure_research_output(self, response: str) -> Dict[str, Any]:
        """Parse research output into structured format."""
        sections = {
            "executive_summary": "",
            "problem_analysis": "",
            "ecosystem_mapping": "",
            "key_findings": [],
            "hypotheses": [],
            "contradictions": "",
            "solutions": [],
            "strategic_implications": "",
            "uncertainties": "",
            "next_directions": ""
        }

        # Parse sections (simple approach)
        current_section = None
        lines = response.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Identify sections
            if 'EXECUTIVE SUMMARY' in line.upper():
                current_section = "executive_summary"
            elif 'PROBLEM ANALYSIS' in line.upper():
                current_section = "problem_analysis"
            elif 'ECOSYSTEM' in line.upper():
                current_section = "ecosystem_mapping"
            elif 'KEY FINDINGS' in line.upper():
                current_section = "key_findings"
            elif 'HYPOTHES' in line.upper():
                current_section = "hypotheses"
            elif 'CONTRADICTION' in line.upper():
                current_section = "contradictions"
            elif 'SOLUTION' in line.upper():
                current_section = "solutions"
            elif 'STRATEGIC' in line.upper():
                current_section = "strategic_implications"
            elif 'UNCERTAINT' in line.upper():
                current_section = "uncertainties"
            elif 'NEXT' in line.upper() and 'DIRECTION' in line.upper():
                current_section = "next_directions"
            elif current_section and line:
                if isinstance(sections[current_section], list):
                    if line.startswith('-') or line.startswith('•'):
                        sections[current_section].append(line[1:].strip())
                    elif len(sections[current_section]) > 0:
                        sections[current_section][-1] += " " + line
                    else:
                        sections[current_section].append(line)
                else:
                    sections[current_section] += line + " "

        return sections

    def _generate_fallback_research(self, query: str) -> str:
        """Generate fallback research when LLM unavailable."""
        return f"""**EXECUTIVE SUMMARY**
Research on '{query}' requires deep investigation into ecosystem dynamics, technical mechanisms, and market context.

**PROBLEM ANALYSIS**
The problem involves understanding complex interdependencies between technology, economics, and human behavior. Key stakeholders include developers, investors, users, and infrastructure providers.

**ECOSYSTEM MAPPING**
This topic sits at the intersection of multiple systems: technical infrastructure, economic incentives, governance mechanisms, and user adoption patterns.

**KEY FINDINGS**
- Finding 1: The space is evolving rapidly with significant innovation
- Finding 2: Multiple competing approaches exist with different tradeoffs
- Finding 3: Incentive alignment remains a critical challenge

**HYPOTHESES**
- Primary: The technology will achieve mainstream adoption through specific use cases
- Alternative: Regulatory challenges may slow growth in certain jurisdictions
- Edge Case: A breakthrough could fundamentally change the landscape

**CONTRADICTIONS IDENTIFIED**
Tension between decentralization ideals and practical usability requirements.

**SOLUTIONS**
1. Gradual Adoption Path
   - Approach: Incremental improvements rather than revolution
   - Tradeoffs: Slower but more sustainable
   - Timeline: 12-24 months

2. Infrastructure First
   - Approach: Build robust foundation before applications
   - Tradeoffs: Delayed gratification but stronger base
   - Timeline: 6-12 months

**STRATEGIC IMPLICATIONS**
Organizations should position for both short-term opportunities and long-term ecosystem development.

**UNCERTAINTIES**
Regulatory landscape, technological breakthroughs, and market sentiment remain key uncertainties.

**NEXT RESEARCH DIRECTIONS**
Investigate specific protocols, interview practitioners, analyze on-chain data."""
