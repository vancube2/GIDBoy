"""GIDBoy Opportunity Agent - Discovers real-world opportunities."""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentState


class OpportunityAgent(BaseAgent):
    """
    Opportunity Agent discovers real-world opportunities from research:
    - Jobs and positions
    - Grants and funding
    - Fellowships
    - DAOs and protocols
    - Consulting angles
    - Strategic partnerships
    """

    def __init__(self, llm_client=None):
        super().__init__("Opportunity", llm_client)
        self.opportunity_prompt = """You are the GIDBoy Opportunity Engine.

RESEARCH CONTEXT:
{research_summary}

USER QUERY:
{query}

Your task: Discover real-world opportunities based on this research.

Search for and identify:

## CRYPTO-NATIVE OPPORTUNITIES

**Jobs & Positions:**
- Research roles at protocols
- Technical positions
- Ecosystem jobs
- DAO contributions

**Grants & Funding:**
- Protocol grants
- Foundation funding
- Research grants
- Ecosystem programs

**DAOs & Communities:**
- Active DAOs in this space
- Contribution opportunities
- Governance participation

**Startups & Projects:**
- Early stage companies
- Pre-launch projects
- Emerging protocols

## TRADITIONAL RESEARCH OPPORTUNITIES

**Academic:**
- Fellowships
- Research positions
- Post-docs
- Research centers

**Industry Research:**
- Think tanks
- Research firms
- Consulting roles
- Industry labs

**Grants (Non-Crypto):**
- Open Society Foundations
- Mozilla Foundation
- Ford Foundation
- Tech ethics grants

## OPPORTUNITY FORMAT

For each opportunity found, provide:

**1. [Opportunity Name]**
- Type: [Job/Grant/Fellowship/DAO/etc]
- Organization: [Name]
- Relevance: [Why this matches the research]
- Requirements: [What's needed to apply]
- Deadline: [If applicable]
- Value: [Compensation/funding amount]
- Difficulty: [1-10 scale]
- Action: [Specific next step]

## STRATEGIC ANALYSIS

**Positioning Angle:**
How should the user position themselves based on this research?

**Competitive Landscape:**
Who else is pursuing these opportunities?

**Timing:**
Why is now the right time?

**Risk Assessment:**
What are the risks and how to mitigate?

**Success Probability:**
Estimate likelihood of success for each opportunity."""

    def process(self, state: AgentState) -> AgentState:
        """Execute opportunity discovery workflow."""
        self.log_reasoning("start", f"Discovering opportunities from: {state.query}")

        # Get research summary from previous agent
        research_summary = state.output.get("research", {})
        research_text = self._format_research_summary(research_summary)

        # Build opportunity prompt
        prompt = self.opportunity_prompt.format(
            research_summary=research_text,
            query=state.query
        )

        # Call LLM
        if self.llm_client:
            response = self.llm_client(
                prompt=prompt,
                temperature=0.4,
                max_tokens=3000
            )
        else:
            response = self._generate_fallback_opportunities(state.query, research_text)

        # Parse opportunities
        opportunities = self._parse_opportunities(response)

        # Update state
        state.output["opportunities"] = opportunities
        state.output["opportunity_raw"] = response
        state.status = "completed"

        self.log_reasoning("complete", f"Found {len(opportunities)} opportunities")

        return state

    def _format_research_summary(self, research: Dict[str, Any]) -> str:
        """Format research for opportunity context."""
        summary = research.get("executive_summary", "")
        key_findings = research.get("key_findings", [])
        ecosystem = research.get("ecosystem_mapping", "")

        return f"""Executive Summary: {summary}

Key Findings:
{chr(10).join(['- ' + f for f in key_findings])}

Ecosystem: {ecosystem}"""

    def _parse_opportunities(self, response: str) -> List[Dict[str, Any]]:
        """Parse opportunities from LLM response."""
        opportunities = []

        # Simple parsing - look for numbered items
        import re

        # Match opportunity patterns
        opp_pattern = r'\*\*\d+\.\s*([^*]+)\*\*\s*\n([^*]+)'
        matches = re.findall(opp_pattern, response, re.DOTALL)

        for match in matches:
            name = match[0].strip()
            details = match[1].strip()

            opp = {
                "name": name,
                "details": details,
                "type": self._detect_type(details),
                "organization": self._extract_org(details),
                "relevance": "",
                "action": ""
            }
            opportunities.append(opp)

        # If no structured opportunities found, create a generic one
        if not opportunities:
            opportunities.append({
                "name": "Research Opportunities",
                "details": "Based on the research, explore positions at leading protocols and research organizations in this space.",
                "type": "research",
                "organization": "Various",
                "relevance": "Matches research interests",
                "action": "Search and apply to relevant positions"
            })

        return opportunities

    def _detect_type(self, details: str) -> str:
        """Detect opportunity type from details."""
        details_lower = details.lower()
        if 'grant' in details_lower:
            return 'grant'
        elif 'job' in details_lower or 'position' in details_lower:
            return 'job'
        elif 'fellowship' in details_lower:
            return 'fellowship'
        elif 'dao' in details_lower:
            return 'dao'
        elif 'bounty' in details_lower:
            return 'bounty'
        return 'other'

    def _extract_org(self, details: str) -> str:
        """Extract organization from details."""
        # Simple extraction - look for common patterns
        import re
        org_patterns = [
            r'Organization:\s*([^\n]+)',
            r'at\s+([A-Z][A-Za-z\s]+)',
            r'from\s+([A-Z][A-Za-z\s]+)'
        ]

        for pattern in org_patterns:
            match = re.search(pattern, details)
            if match:
                return match.group(1).strip()

        return "TBD"

    def _generate_fallback_opportunities(self, query: str, research: str) -> str:
        """Generate fallback opportunities."""
        return f"""**1. Protocol Research Grants**
- Type: Grant
- Organization: Leading protocols in {query[:30]}...
- Relevance: Direct application of research expertise
- Requirements: Research proposal, track record
- Deadline: Rolling applications
- Value: $5K-$250K
- Difficulty: 6/10
- Action: Draft research proposal and submit to 3-5 protocols

**2. Ecosystem Research Positions**
- Type: Job/Contract
- Organization: Research DAOs and analytics firms
- Relevance: Research skills directly applicable
- Requirements: Portfolio of research, technical understanding
- Deadline: Ongoing
- Value: Competitive salary or contract rates
- Difficulty: 5/10
- Action: Prepare research portfolio and reach out

**3. Independent Research Fellowships**
- Type: Fellowship
- Organization: Web3 foundations, academic institutions
- Relevance: Support independent research
- Requirements: Research plan, credentials
- Deadline: Quarterly cycles
- Value: Stipend + research budget
- Difficulty: 7/10
- Action: Identify fellowship programs and apply

**4. Consulting Opportunities**
- Type: Consulting/Advisory
- Organization: Startups, VCs, protocols
- Relevance: Expertise from research
- Requirements: Domain knowledge, network
- Deadline: As needed
- Value: Hourly or project-based
- Difficulty: 4/10
- Action: Position as expert advisor

**STRATEGIC ANALYSIS**

**Positioning Angle:**
Position as deep researcher with expertise in {query[:30]}... ecosystem.

**Competitive Landscape:**
Moderate competition, differentiation through depth of analysis.

**Timing:**
Research-driven insights currently in high demand.

**Risk Assessment:**
Low risk, multiple pathways available.

**Success Probability:**
High if research is converted into positioning and content."""
