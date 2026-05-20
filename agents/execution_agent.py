"""GIDBoy Execution Agent - Turns intelligence into action."""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentState


class ExecutionAgent(BaseAgent):
    """
    Execution Agent assists with:
    - Applications
    - Outreach
    - Grant proposals
    - Fellowship applications
    - Strategic emails
    - Partnership pitches
    """

    def __init__(self, llm_client=None):
        super().__init__("Execution", llm_client)
        self.execution_prompt = """You are the GIDBoy Execution Engine.

RESEARCH CONTEXT:
{research_summary}

OPPORTUNITIES TO PURSUE:
{opportunity_summary}

CONTENT AVAILABLE:
{content_summary}

USER QUERY:
{query}

Your task: Turn this intelligence into concrete, actionable execution.

## EXECUTION SUPPORT

Based on the opportunities and research, provide:

### 1. PRIORITIZED ACTION PLAN

**Immediate (This Week):**
- What to do first
- Why this matters now
- Expected outcome

**Short-term (Next 2-4 Weeks):**
- Key actions
- Resources needed
- Success criteria

**Medium-term (1-3 Months):**
- Strategic moves
- Positioning goals
- Milestones

### 2. OUTREACH TEMPLATES

**Cold Outreach Email:**
- Subject line
- Opening hook
- Value proposition
- Call to action
- Professional close

**Follow-up Sequence:**
- Day 3 follow-up
- Day 7 follow-up
- Day 14 final attempt

**LinkedIn Connection Request:**
- Personalized note
- Context reference
- Soft CTA

### 3. APPLICATION SUPPORT

**Grant Proposal Template:**
- Executive summary
- Problem statement
- Proposed solution
- Budget outline
- Timeline
- Team/experience
- Expected outcomes

**Job Application Strategy:**
- Resume optimization
- Cover letter approach
- Portfolio highlights
- Interview talking points

**Fellowship Application:**
- Research proposal structure
- Previous work showcase
- Future research plan
- Letters of support strategy

### 4. POSITIONING MATERIALS

**Personal Bio/About:**
- Positioning statement
- Key credentials
- Research focus
- Value proposition

**One-Pager:**
- Who you are
- What you do
- Why it matters
- Call to action

## CUSTOMIZATION GUIDANCE

For each template, explain:
- How to customize for specific targets
- What research findings to reference
- How to position the unique angle
- What tone to use

## SUCCESS METRICS

**Response Rate Targets:**
- Cold email: 20-30%
- LinkedIn: 40-50%
- Warm intro: 60-70%

**Conversion Tracking:**
- How to track applications
- How to measure progress
- When to pivot approach

## OUTPUT FORMAT

Provide ready-to-use templates with [brackets] for customization."""

    def process(self, state: AgentState) -> AgentState:
        """Execute planning workflow."""
        self.log_reasoning("start", f"Planning execution for: {state.query}")

        # Get all previous outputs
        research = state.output.get("research", {})
        opportunities = state.output.get("opportunities", [])
        content = state.output.get("content", {})

        # Format context
        research_text = self._format_research(research)
        opp_text = self._format_opportunities(opportunities)
        content_text = self._format_content(content)

        # Build execution prompt
        prompt = self.execution_prompt.format(
            research_summary=research_text,
            opportunity_summary=opp_text,
            content_summary=content_text,
            query=state.query
        )

        # Call LLM
        if self.llm_client:
            response = self.llm_client(
                prompt=prompt,
                temperature=0.4,
                max_tokens=4000
            )
        else:
            response = self._generate_fallback_execution(state.query, opportunities)

        # Parse execution plan
        execution_plan = self._parse_execution(response)

        # Update state
        state.output["execution"] = execution_plan
        state.output["execution_raw"] = response
        state.status = "completed"

        self.log_reasoning("complete", "Execution plan generated")

        return state

    def _format_research(self, research: Dict[str, Any]) -> str:
        """Format research for execution context."""
        return f"""Executive Summary: {research.get('executive_summary', '')}
Key Findings: {', '.join(str(f) for f in research.get('key_findings', [])[:3])}
Strategic Implications: {research.get('strategic_implications', '')}"""

    def _format_opportunities(self, opportunities: List[Dict[str, Any]]) -> str:
        """Format opportunities for execution context."""
        if not opportunities:
            return "No opportunities specified"

        texts = []
        for opp in opportunities[:3]:
            texts.append(f"- {opp.get('name', 'N/A')} ({opp.get('type', 'N/A')})")
        return "\n".join(texts)

    def _format_content(self, content: Dict[str, Any]) -> str:
        """Format content for execution context."""
        return f"""Thread available: {bool(content.get('thread'))}
LinkedIn post available: {bool(content.get('linkedin'))}
Brief available: {bool(content.get('brief'))}"""

    def _parse_execution(self, response: str) -> Dict[str, Any]:
        """Parse execution plan from response."""
        import re

        plan = {
            "immediate_actions": [],
            "short_term_actions": [],
            "medium_term_actions": [],
            "email_template": "",
            "linkedin_template": "",
            "grant_template": "",
            "positioning_bio": ""
        }

        # Extract sections
        sections = [
            ("immediate_actions", r"Immediate.*?Week.*?\n(.*?)(?=Short-term|###|$)"),
            ("email_template", r"Cold Outreach Email.*?\n(.*?)(?=Follow-up|###|$)"),
            ("linkedin_template", r"LinkedIn.*?\n(.*?)(?=###|$)"),
        ]

        for key, pattern in sections:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                plan[key] = match.group(1).strip()

        return plan

    def _generate_fallback_execution(self, query: str, opportunities: List[Dict[str, Any]]) -> str:
        """Generate fallback execution plan."""
        opp_names = [o.get('name', 'Opportunity') for o in opportunities[:2]]

        return f"""### PRIORITIZED ACTION PLAN

**Immediate (This Week):**
1. Review and customize the research findings for {opp_names[0] if opp_names else 'target organization'}
2. Prepare outreach materials
3. Identify 3-5 key contacts

**Short-term (Next 2-4 Weeks):**
1. Execute outreach campaign
2. Follow up on initial contacts
3. Refine positioning based on feedback

**Medium-term (1-3 Months):**
1. Secure initial meetings/opportunities
2. Build relationship pipeline
3. Convert research into contracts/grants

### OUTREACH TEMPLATES

**Cold Email:**
Subject: Research on {query[:40]}...

Hi [Name],

I've been researching {query[:30]}... and came across your work on [specific project].

My analysis revealed [key finding] that may be relevant to your work on [area].

Would you be open to a brief conversation about [specific angle]?

Best,
[Your name]

**LinkedIn Connection:**
Hi [Name], I've been analyzing {query[:30]}... and noticed your expertise in [area]. Would love to connect and share insights.

### APPLICATION SUPPORT

**Grant Proposal Structure:**
- Executive Summary: Reference key findings from research
- Problem: What gap does this address?
- Solution: How does your research help?
- Budget: Realistic breakdown
- Timeline: Achievable milestones

**Positioning Bio:**
Researcher specializing in [area]. Recent work includes [key finding]. Seeking to contribute to [type of organization].

### SUCCESS METRICS

- Response rate: Target 25%
- Meeting conversion: Target 50%
- Opportunity conversion: Target 30%

Track all outreach and follow up systematically."""
