"""GIDBoy Content Agent - Converts intelligence into authority-building content."""
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentState


class ContentAgent(BaseAgent):
    """
    Content Agent transforms research into:
    - X/Twitter threads
    - LinkedIn posts
    - Research reports
    - Intelligence briefs
    - Ecosystem analyses
    """

    def __init__(self, llm_client=None):
        super().__init__("Content", llm_client)
        self.content_prompt = """You are the GIDBoy Content Engine.

RESEARCH TO CONVERT:
{research_summary}

OPPORTUNITIES CONTEXT:
{opportunity_summary}

Your task: Convert this intelligence into authority-building content.

The content must:
- Reflect original thinking
- Contain strong insights
- Avoid generic AI tone
- Position the user as a serious research analyst
- Be ready to publish

## CONTENT PACKAGE

### 1. X/TWITTER THREAD

**Structure (8-12 tweets):**

Tweet 1 (Hook):
- Attention-grabbing opening
- Question or bold statement
- Must make reader want to read more

Tweet 2-3 (Context):
- What people think they know
- The surface narrative
- Set up the insight

Tweet 4-6 (Core Insights):
- Tweet 4: First key finding with evidence
- Tweet 5: Second key finding with mechanism
- Tweet 6: Third key finding with implication

Tweet 7-8 (Analysis):
- Pattern recognition
- Historical parallel
- Why this matters now

Tweet 9-10 (Implications):
- First-order effects
- Second-order effects
- Who benefits

Tweet 11 (Actionable):
- What should people do?
- How to position?
- Specific recommendation

Tweet 12 (Close):
- Memorable closing thought
- Follow for more
- Engagement CTA

### 2. LINKEDIN POST

**Structure:**
- Headline that stands out in feed
- Hook paragraph (2-3 sentences max)
- Body with insights (use line breaks)
- Data/evidence points
- Strategic implication
- Personal angle
- Call to action

**Tone:** Professional, thoughtful, authoritative

### 3. INTELLIGENCE BRIEF (1-pager)

**Structure:**
- **EXECUTIVE SUMMARY** (3-4 sentences)
- **KEY FINDINGS** (bullet points with evidence)
- **ANALYSIS** (what it means)
- **IMPLICATIONS** (what happens next)
- **ACTIONABLE RECOMMENDATIONS** (what to do)
- **SOURCES** (for credibility)

### 4. RESEARCH REPORT (Long-form)

**Structure:**
- Title
- Abstract
- Introduction
- Methodology
- Findings
- Analysis
- Implications
- Recommendations
- Conclusion

## CONTENT QUALITY CHECKLIST

- [ ] Original insight, not recycled narrative
- [ ] Specific data points and evidence
- [ ] Clear reasoning chain
- [ ] Actionable takeaways
- [ ] Professional tone
- [ ] No engagement bait
- [ ] No generic crypto content
- [ ] Positions author as expert

## OUTPUT FORMAT

Provide all content formats ready to use."""

    def process(self, state: AgentState) -> AgentState:
        """Execute content generation workflow."""
        self.log_reasoning("start", f"Generating content for: {state.query}")

        # Get research and opportunities
        research = state.output.get("research", {})
        opportunities = state.output.get("opportunities", [])

        research_text = self._format_research(research)
        opp_text = self._format_opportunities(opportunities)

        # Build content prompt
        prompt = self.content_prompt.format(
            research_summary=research_text,
            opportunity_summary=opp_text
        )

        # Call LLM
        if self.llm_client:
            response = self.llm_client(
                prompt=prompt,
                temperature=0.5,
                max_tokens=4000
            )
        else:
            response = self._generate_fallback_content(state.query, research)

        # Parse content
        content_package = self._parse_content(response)

        # Update state
        state.output["content"] = content_package
        state.output["content_raw"] = response
        state.status = "completed"

        self.log_reasoning("complete", "Content package generated")

        return state

    def _format_research(self, research: Dict[str, Any]) -> str:
        """Format research for content context."""
        return f"""Executive Summary: {research.get('executive_summary', '')}

Key Findings:
{chr(10).join(['- ' + str(f) for f in research.get('key_findings', [])])}

Strategic Implications: {research.get('strategic_implications', '')}

Solutions: {chr(10).join([str(s) for s in research.get('solutions', [])[:2]])}"""

    def _format_opportunities(self, opportunities: List[Dict[str, Any]]) -> str:
        """Format opportunities for content context."""
        if not opportunities:
            return "No specific opportunities identified."

        texts = []
        for opp in opportunities[:3]:
            texts.append(f"- {opp.get('name', 'N/A')}: {opp.get('type', 'N/A')}")
        return "\n".join(texts)

    def _parse_content(self, response: str) -> Dict[str, Any]:
        """Parse content package from response."""
        import re

        content = {
            "thread": "",
            "linkedin": "",
            "brief": "",
            "report": ""
        }

        # Extract sections
        sections = [
            ("thread", r"X/TWITTER THREAD(.+?)(?=LINKEDIN|INTELLIGENCE BRIEF|$)"),
            ("linkedin", r"LINKEDIN POST(.+?)(?=INTELLIGENCE BRIEF|RESEARCH REPORT|$)"),
            ("brief", r"INTELLIGENCE BRIEF(.+?)(?=RESEARCH REPORT|$)"),
            ("report", r"RESEARCH REPORT(.+?)$")
        ]

        for key, pattern in sections:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                content[key] = match.group(1).strip()

        return content

    def _generate_fallback_content(self, query: str, research: Dict[str, Any]) -> str:
        """Generate fallback content."""
        key_findings = research.get('key_findings', ['Research reveals key insights'])
        summary = research.get('executive_summary', 'Research completed on ' + query)

        return f"""### X/TWITTER THREAD

Tweet 1: Most people misunderstand {query[:40]}...

Here's what the research actually shows 🧵

Tweet 2: The surface narrative: [what everyone says]

Tweet 3: The reality: {summary[:100]}...

Tweet 4: Key finding: {key_findings[0] if key_findings else 'Significant insights discovered'}

Tweet 5: This matters because it changes how we think about the ecosystem.

Tweet 6: The implication: opportunity exists for those who understand this.

Tweet 7: What to do: Position around these insights.

Tweet 8: The deeper I go, the more convinced I am that this is undervalued.

Tweet 9: Follow for more research insights.

### LINKEDIN POST

**Headline:** What I learned researching {query[:40]}...

After weeks of analysis, three things became clear:

1. The surface narrative misses the real dynamics
2. Ecosystem incentives drive unexpected behavior
3. Opportunity exists in the gaps

{summary[:150]}...

This research has implications for:
- Protocol designers
- Investors
- Builders
- Researchers

The key is understanding not just what is happening, but why.

What's your take on this?

#research #analysis #{query.split()[0]}

### INTELLIGENCE BRIEF

**EXECUTIVE SUMMARY**
{summary}

**KEY FINDINGS**
{chr(10).join(['- ' + str(f) for f in key_findings[:3]])}

**IMPLICATIONS**
Research reveals strategic opportunities in this ecosystem.

**RECOMMENDATIONS**
1. Position around identified insights
2. Engage with key ecosystem players
3. Monitor developments closely

**NEXT STEPS**
Convert research into positioning and outreach."""
